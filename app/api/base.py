# Standard library imports
import inspect
import uuid
from datetime import datetime as dt
from typing import Optional

# Third party imports
from flask import Request, g, request
from flask_classful import FlaskView
from flask_sqlalchemy import DefaultMeta
from marshmallow.exceptions import ValidationError as SchemaValidationError
from marshmallow.schema import SchemaMeta
from webargs.flaskparser import parser, use_args

# Local application imports
from app.utils import localize_text

# Local folder imports
from .const import DEFAULT_ITEMS_PER_PAGE
from .error import BadRequestError, NotFoundError, ValidationError
from .representation import output_json
from .response import APIResponse
from .schema import APIPaginationDataSchema, BaseSchema


class BaseAPI(FlaskView):
    base_args = ["args"]
    representations = {
        "application/json": output_json,
        "flask-classful/default": output_json,
    }
    model: Optional[DefaultMeta] = None
    schema: Optional[SchemaMeta] = None
    route_prefix = "/api/"
    route_base: Optional[str] = None
    method_dashified = True
    api_version: Optional[str] = None
    trailing_slash = False
    service: Optional[type] = None

    def _add_api_version(self):
        if getattr(g, "api_version", None) is None:
            g.api_version = self.api_version

    def _log_start_time(self):
        if getattr(g, "request_start_time", None) is None:
            g.request_start_time = dt.now()

    def _service(self):
        assert inspect.isclass(self.service)
        return self.service(model=self.model)

    @staticmethod
    def _add_params():
        if getattr(g, "request_params", None) is None:
            g.request_params = dict(request.args)

    @staticmethod
    def _update_params(data: dict):
        assert isinstance(data, dict)
        request_params = getattr(g, "request_params", None)
        if request_params is None:
            g.request_params = data
        else:
            g.request_params = dict(request_params, **data)

    @staticmethod
    def _add_request_id():
        request_id = uuid.uuid4()
        g.request_id = request_id

    def before_request(self, name, *args, **kwargs):
        self._log_start_time()
        self._add_request_id()
        self._add_api_version()
        self._add_params()

    def _get_item_by_id_or_not_found(self, id: int):
        try:
            item = self._service().get_by_id(id)
        except TypeError:
            raise BadRequestError
        if item is None:
            raise NotFoundError
        return item

    @staticmethod
    @parser.error_handler
    def _handle_validation_error(
        error: SchemaValidationError,
        req: Request,
        schema: BaseSchema,
        *,
        error_status_code: int,
        error_headers: dict,
    ):
        """Handles webargs validation error"""
        assert hasattr(error, "messages") and error.messages is not None
        error_messages = error.messages
        errors = (
            error_messages if isinstance(error_messages, list) else [error_messages]
        )
        raise ValidationError(errors=errors)

    def post(self):
        request_body = request.get_json()
        if request_body is None:
            message = localize_text("empty_post_body")
            raise BadRequestError(message=message)
        try:
            data = self.schema().load(request_body)
        except SchemaValidationError as err:
            raise ValidationError(errors=err.messages)
        item = self._service().create(data)
        return APIResponse().create_response(item=item, schema=self.schema)

    def get(self, id: int):
        self._update_params({"id": id})
        schema = self.schema
        assert schema is not None and issubclass(schema, BaseSchema)
        item = self._get_item_by_id_or_not_found(id)
        return APIResponse().create_response(item=item, schema=schema)

    @use_args(APIPaginationDataSchema(), location="query")
    def index(self, args):
        items_per_page: int = args.get("items_per_page") or DEFAULT_ITEMS_PER_PAGE
        page_index: Optional[int] = args.get("page_index")
        start_index: Optional[int] = args.get("start_index")
        if page_index is None and start_index is None:
            error_message = localize_text("missing_page_and_start_index")
            raise BadRequestError(message=error_message)
        query = self._service().list()
        return APIResponse().create_paginated_response(
            query=query,
            items_per_page=items_per_page,
            page_index=page_index,
            start_index=start_index,
            schema=self.schema,
        )

    def put(self, id: int):
        self._update_params({"id": id})
        request_body = request.get_json()
        if request_body is None:
            message = localize_text("empty_put_body")
            raise BadRequestError(message=message)
        schema = self.schema
        assert schema is not None and issubclass(schema, BaseSchema)
        try:
            data = schema().load(request_body)
        except SchemaValidationError as err:
            raise ValidationError(errors=err.messages)
        item = self._get_item_by_id_or_not_found(id)
        item = self._service().update(item, data)
        return APIResponse().create_response(item=item, schema=schema)

    def delete(self, id: int):
        self._update_params({"id": id})
        item = self._get_item_by_id_or_not_found(id)
        self._service().delete(item)
        return APIResponse().create_success_response(
            model=self.model, method=request.method
        )
