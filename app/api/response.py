# Standard library imports
import math
from typing import Optional, Tuple

# Third party imports
from flask import g
from flask_sqlalchemy import DefaultMeta
from marshmallow.schema import SchemaMeta
from sqlalchemy.orm import Query

# Local folder imports
from ..utils import localize_text
from .const import HttpMethodVerbs
from .error import APIError
from .model import Model
from .schema import (
    APIErrorResponseSchema,
    APIPaginatedResponseSchema,
    APISingleResponseSchema,
    APISuccessResponseSchema,
    BaseSchema,
)


class APIResponse(object):
    @staticmethod
    def _create_response(
        data: Optional[dict] = None,
        success: Optional[dict] = None,
        error: Optional[dict] = None,
    ) -> dict:
        assert data is not None or success is not None or error is not None
        assert success is None or error is None

        if data is not None:
            assert success is None

        api_version = getattr(g, "api_version", "")
        request_id = getattr(g, "request_id", "")
        request_params = getattr(g, "request_params", {})

        response = dict(api_version=api_version, id=request_id, params=request_params)

        if error is not None:
            response["error"] = error
        elif data is not None:
            response["data"] = data
        elif success is not None:
            response["success"] = success

        return response

    @staticmethod
    def _get_pagination_params(
        page_index: Optional[int],
        start_index: Optional[int],
        items_per_page: int,
        total_items: int,
    ) -> Tuple[Optional[int], int, Optional[int], int]:
        if page_index is not None:
            assert isinstance(page_index, int)
            assert page_index > 0

        if start_index is not None:
            assert isinstance(start_index, int)
            assert start_index > 0

        # Compute total pages
        if page_index is not None and start_index is None:
            # Page-based pagination
            total_pages = math.ceil(total_items / items_per_page)
        elif start_index is not None:
            # Item-based pagination
            if start_index <= total_items:
                total_pages = math.ceil((total_items - start_index) / items_per_page)
            else:
                total_pages = 0

        # Compute start, stop (& page) index
        if page_index is not None:
            # Page-based pagination
            if start_index is None:
                start_index = (items_per_page * (page_index - 1)) + 1 or 1
                stop_index = items_per_page * page_index
            else:
                # Page- & Item-based pagination
                start_index = (items_per_page * (page_index - 1)) + start_index
                stop_index = (start_index + items_per_page) - 1
        elif start_index is not None:
            # Item-based pagination
            stop_index = (start_index + items_per_page) - 1
            page_index = math.floor(start_index / items_per_page) + 1

        return start_index, stop_index, page_index, total_pages

    def create_error_response(self, api_error: APIError) -> Tuple[dict, int]:
        assert isinstance(api_error, APIError)
        error_code = api_error.code
        assert isinstance(error_code, int)
        error = dict(
            code=error_code, message=api_error.message, errors=api_error.errors
        )
        response = self._create_response(error=error)
        result = APIErrorResponseSchema().dump(response)
        return result, error_code

    def create_success_response(self, model: DefaultMeta, method: str) -> dict:
        assert issubclass(model, Model)
        assert isinstance(method, str)
        model_name = localize_text(model.__name__.lower()).capitalize()
        method_verb = HttpMethodVerbs[method].done()
        message = f"{model_name} {localize_text('successfully')} {(method_verb)}"
        success = dict(message=message)
        response = self._create_response(success=success)
        result = APISuccessResponseSchema().dump(response)
        return result

    def create_response(self, item: Model, schema: SchemaMeta) -> dict:
        # Validate
        assert isinstance(item, Model)
        assert issubclass(schema, BaseSchema)

        # Serialize
        data = schema(many=False).dump(item)

        response = self._create_response(data=data)

        return APISingleResponseSchema().dump(response)

    def create_paginated_response(
        self,
        items_per_page: int,
        query: Query,
        schema: SchemaMeta,
        page_index: Optional[int] = None,
        start_index: Optional[int] = None,
    ) -> dict:
        # Validate
        assert isinstance(query, Query)
        assert issubclass(schema, BaseSchema)
        assert isinstance(items_per_page, int)

        total_items = query.count()
        start_index, stop_index, page_index, total_pages = self._get_pagination_params(
            page_index, start_index, items_per_page, total_items
        )

        assert isinstance(start_index, int)

        # Slice
        items = query.slice(start_index - 1, stop_index)
        current_item_count = items.count()

        # Serialize
        items = schema(many=True).dump(items)

        # Prepare result
        data = dict(
            items_per_page=items_per_page,
            current_item_count=current_item_count,
            page_index=page_index,
            start_index=start_index,
            total_items=total_items,
            total_pages=total_pages,
            items=items,
        )

        response = self._create_response(data=data)

        return APIPaginatedResponseSchema().dump(response)
