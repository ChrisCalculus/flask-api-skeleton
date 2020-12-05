# Standard library imports
import math
from typing import Any, Dict, Optional

# Third party imports
import pytest
from marshmallow import fields
from pytest import fixture

# Local folder imports
from .error import APIError
from .model import Model
from .response import APIResponse
from .schema import BaseSchema

API_RESPONSE_KEYS = ["params", "apiVersion", "id", "duration"]


class DummyError(APIError):
    code = 400

    def __init__(self, code=None, **kwargs):
        super().__init__(**kwargs)
        self.code = code


@fixture
def dummy_api_error():
    def _dummy_api_error(code: int = 400):
        return DummyError(code=code)

    return _dummy_api_error


@fixture
def dummy_schema():
    class DummySchema(BaseSchema):
        id = fields.Int()

    return DummySchema


def test_create_responses(app_context):
    required_output_params = ["api_version", "id", "params"]
    possible_output_params = required_output_params + ["data", "error", "success"]

    # Check response
    data: Optional[Dict[str, Any]] = dict()
    success: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

    api_response = APIResponse()
    response = api_response._create_response(data, success, error)

    # Check output format
    assert isinstance(response, dict)
    # Check if required params are present
    assert all(k in response.keys() for k in required_output_params) is True
    # Prevent additional / unknown params
    assert all(k in possible_output_params for k in response.keys()) is True

    # Error response
    data = None
    success = None
    error = dict()
    response = api_response._create_response(data, success, error)
    assert (
        response.get("error") == error
        and response.get("data") == data
        and response.get("success") == success
    )

    # Data response
    data = dict()
    success = None
    error = None
    response = api_response._create_response(data, success, error)
    assert (
        response.get("error") == error
        and response.get("data") == data
        and response.get("success") == success
    )

    # Success response
    data = None
    success = dict()
    error = None
    response = api_response._create_response(data, success, error)
    assert (
        response.get("error") == error
        and response.get("data") == data
        and response.get("success") == success
    )

    # Prevent error and success
    data = None
    success = dict()
    error = dict()
    with pytest.raises(AssertionError):
        api_response._create_response(data, success, error)

    # Prevent error and data
    data = None
    success = dict()
    error = dict()
    with pytest.raises(AssertionError):
        api_response._create_response(data, success, error)

    # Prevent success and data
    data = dict()
    success = dict()
    error = None
    with pytest.raises(AssertionError):
        api_response._create_response(data, success, error)


def test_get_pagination_params():
    api_response = APIResponse()

    # page_index == 1 without start_index
    page_index, start_index, items_per_page, total_items = 1, None, 5, 25
    (
        start_index,
        stop_index,
        page_index,
        total_pages,
    ) = api_response._get_pagination_params(  # type: ignore
        page_index, start_index, items_per_page, total_items
    )
    assert start_index == 1
    assert stop_index == 5
    assert page_index == 1
    assert total_pages == 5

    # page_index > 1 without start_index
    page_index, start_index, items_per_page, total_items = 2, None, 5, 25
    (
        start_index,
        stop_index,
        page_index,
        total_pages,
    ) = api_response._get_pagination_params(  # type: ignore
        page_index, start_index, items_per_page, total_items
    )
    assert start_index == 6
    assert stop_index == 10
    assert page_index == 2
    assert total_pages == 5

    # page_index > total_pages
    page_index, start_index, items_per_page, total_items = 6, None, 5, 25
    (
        start_index,
        stop_index,
        page_index,
        total_pages,
    ) = api_response._get_pagination_params(  # type: ignore
        page_index, start_index, items_per_page, total_items
    )
    assert start_index == 26
    assert stop_index == 30
    assert page_index == 6
    assert total_pages == 5

    # page_index == 0
    page_index, start_index, items_per_page, total_items = 0, None, 5, 25
    with pytest.raises(AssertionError):
        api_response._get_pagination_params(
            page_index, start_index, items_per_page, total_items
        )

    # start_index == 0
    page_index, start_index, items_per_page, total_items = None, 0, 5, 25  # type: ignore
    with pytest.raises(AssertionError):
        api_response._get_pagination_params(
            page_index, start_index, items_per_page, total_items
        )

    # start_index == 1 without page_index
    page_index, start_index, items_per_page, total_items = None, 1, 5, 25  # type: ignore
    (
        start_index,
        stop_index,
        page_index,
        total_pages,
    ) = api_response._get_pagination_params(  # type: ignore
        page_index, start_index, items_per_page, total_items
    )
    assert start_index == 1
    assert stop_index == 5
    assert page_index == 1
    assert total_pages == 5

    # start_index > 1 without page_index
    page_index, start_index, items_per_page, total_items = None, 2, 5, 25  # type: ignore
    (
        start_index,
        stop_index,
        page_index,
        total_pages,
    ) = api_response._get_pagination_params(  # type: ignore
        page_index, start_index, items_per_page, total_items
    )
    assert start_index == 2
    assert stop_index == 6
    assert page_index == 1
    assert total_pages == 5

    # start_index > total_items
    page_index, start_index, items_per_page, total_items = None, 26, 5, 25  # type: ignore
    (
        start_index,
        stop_index,
        page_index,
        total_pages,
    ) = api_response._get_pagination_params(  # type: ignore
        page_index, start_index, items_per_page, total_items
    )
    assert start_index == 26
    assert stop_index == 30
    assert page_index == 6
    assert total_pages == 0

    # page_index == 1 with start_index == 1
    page_index, start_index, items_per_page, total_items = 1, 1, 5, 25
    (
        start_index,
        stop_index,
        page_index,
        total_pages,
    ) = api_response._get_pagination_params(  # type: ignore
        page_index, start_index, items_per_page, total_items
    )
    assert start_index == 1
    assert stop_index == 5
    assert page_index == 1
    assert total_pages == 5

    # page_index == 1 with start_index == 6
    page_index, start_index, items_per_page, total_items = 1, 6, 5, 25
    (
        start_index,
        stop_index,
        page_index,
        total_pages,
    ) = api_response._get_pagination_params(  # type: ignore
        page_index, start_index, items_per_page, total_items
    )
    assert start_index == 6
    assert stop_index == 10
    assert page_index == 1
    assert total_pages == 4

    # page_index == 2 with start_index == 6
    page_index, start_index, items_per_page, total_items = 2, 6, 5, 25
    (
        start_index,
        stop_index,
        page_index,
        total_pages,
    ) = api_response._get_pagination_params(  # type: ignore
        page_index, start_index, items_per_page, total_items
    )
    assert start_index == 11
    assert stop_index == 15
    assert page_index == 2
    assert total_pages == 4

    # page_index > total_pages with start_index > total_items
    page_index, start_index, items_per_page, total_items = 2, 26, 5, 25
    (
        start_index,
        stop_index,
        page_index,
        total_pages,
    ) = api_response._get_pagination_params(  # type: ignore
        page_index, start_index, items_per_page, total_items
    )
    assert start_index == 31
    assert stop_index == 35
    assert page_index == 2
    assert total_pages == 0

    # page_index == 0 and start_index == 0
    page_index, start_index, items_per_page, total_items = 0, 0, 5, 25
    with pytest.raises(AssertionError):
        api_response._get_pagination_params(
            page_index, start_index, items_per_page, total_items
        )


def test_created_error_response(app_context, dummy_api_error: APIError):
    api_response = APIResponse()

    error_code = 400
    dummy_bad_request_api_error = dummy_api_error(code=error_code)  # type: ignore
    detailed_response_key = "error"
    response, error_code = api_response.create_error_response(
        dummy_bad_request_api_error
    )
    assert isinstance(response, dict) and error_code == error_code
    # Check if required response params are present
    error_response_keys = API_RESPONSE_KEYS + [detailed_response_key]
    assert all(k in response.keys() for k in error_response_keys) is True
    # Check if required detail response params are present
    detailed_response_keys = ["errors", "code", "message"]
    assert (
        all(
            k in response.get(detailed_response_key, {}).keys()
            for k in detailed_response_keys
        )
        is True
    )


def test_created_success_response(app_context):
    api_response = APIResponse()

    model = Model
    delete_method = "DELETE"
    detailed_response_key = "success"
    response = api_response.create_success_response(model, delete_method)
    assert isinstance(response, dict)
    # Check if required response params are present
    success_response_keys = API_RESPONSE_KEYS + [detailed_response_key]
    assert all(k in response.keys() for k in success_response_keys) is True
    # Check if required detail response params are present
    detailed_response_keys = ["message"]
    assert (
        all(
            k in response.get(detailed_response_key, {}).keys()
            for k in detailed_response_keys
        )
        is True
    )


def test_create_response(app_context, dummy_model_object, dummy_schema):
    api_response = APIResponse()

    item = dummy_model_object()
    schema = dummy_schema
    response = api_response.create_response(item, schema)
    assert isinstance(response, dict)


def test_create_paginated_response(
    db_session, dummy_model, dummy_model_object, dummy_schema,
):
    api_response = APIResponse()

    items_per_page = 5
    query = dummy_model.query
    schema = dummy_schema
    page_index = 1
    start_index = None
    detailed_response_key = "data"
    no_created_items = 10

    # Create 10 items
    for _i in range(no_created_items):
        item = dummy_model_object()
        db_session.add(item)
    db_session.commit()

    response = api_response.create_paginated_response(
        items_per_page, query, schema, page_index, start_index
    )
    assert isinstance(response, dict)
    # Check if required response params are present
    data_response_keys = API_RESPONSE_KEYS + [detailed_response_key]
    assert all(k in response.keys() for k in data_response_keys) is True
    # Check if required detail response params are present
    detailed_response_keys = [
        "pageIndex",
        "totalPages",
        "totalItems",
        "currentItemCount",
        "items",
        "itemsPerPage",
        "startIndex",
    ]
    assert (
        all(
            k in response.get(detailed_response_key, {}).keys()
            for k in detailed_response_keys
        )
        is True
    )
    response_data = response.get("data", {})
    response_page = response_data.get("pageIndex")
    assert response_page == 1
    response_items = response_data.get("items", [])
    assert all(isinstance(i, dict) for i in response_items)
    response_current_item_count = response_data.get("currentItemCount")
    assert isinstance(response_current_item_count, int)
    assert (
        isinstance(response_items, list)
        and len(response_items) == items_per_page == response_current_item_count
    )
    response_total_items = response_data.get("totalItems")
    assert (
        isinstance(response_total_items, int)
        and response_total_items == no_created_items
    )
    response_total_pages = response_data.get("totalPages")
    assert response_total_pages == math.ceil(no_created_items / items_per_page)
    response_start_index = response_data.get("startIndex")
    assert response_start_index == 1
