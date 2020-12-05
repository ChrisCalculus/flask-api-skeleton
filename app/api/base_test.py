# Standard library imports
import inspect
import math
import uuid
from datetime import datetime as dt

# Third party imports
import pytest
from flask import current_app, g

# Local application imports
from app.api.error import BadRequestError, NotFoundError, ValidationError


def test_add_api_version(app_context, dummy_api):
    assert getattr(g, "api_version", None) is None
    api_version = "1.0"
    api = dummy_api(api_version=api_version)
    api._add_api_version()
    assert getattr(g, "api_version", None) == api_version


def test_log_start_time(app_context, dummy_api):
    assert getattr(g, "request_start_time", None) is None
    api = dummy_api()
    api._log_start_time()
    assert isinstance(getattr(g, "request_start_time", None), dt)


def test_service(
    app_context, dummy_api, dummy_crud_model, dummy_service, dummy_service_object
):
    model = dummy_crud_model
    service = dummy_service
    api = dummy_api(model=model, service=service)
    service_obj = api._service()
    assert getattr(service_obj, "model", None) == model

    # Test service instance
    service = dummy_service_object(model=model)
    api = dummy_api(model=model, service=service)

    with pytest.raises(AssertionError):
        api._service()


def test_add_params(client, dummy_api):
    def test_route_1():
        return "OK", 200

    endpoint = "/"
    current_app.add_url_rule(endpoint, test_route_1.__name__, view_func=test_route_1)

    data = dict(a="1", b="2")

    assert getattr(g, "request_params", None) is None
    client.get(endpoint, query_string=data)
    dummy_api()._add_params()
    assert g.request_params == data

    # Test request_params is not None
    g.request_params == data
    changed_data = dict(c="3")
    client.get(endpoint, query_string=changed_data)
    dummy_api()._add_params()
    assert g.request_params == data


def test_update_params(client, dummy_api):
    # No previous request_params
    data = dict(a="1", b="2")

    api = dummy_api()

    api._update_params(data)
    assert g.request_params == data

    # Update request_params
    update_data = dict(a="3", c="4")
    api._update_params(update_data)
    updated_result = dict(data, **update_data)
    assert g.request_params == updated_result

    # Update with None
    with pytest.raises(AssertionError):
        api._update_params(None)


def test_add_request_id(client, dummy_api):
    def test_route_1():
        return "OK", 200

    endpoint = "/"
    current_app.add_url_rule(endpoint, test_route_1.__name__, view_func=test_route_1)
    assert getattr(g, "request_id", None) is None
    client.get(endpoint)
    dummy_api()._add_request_id()
    first_request_id = getattr(g, "request_id", None)
    assert first_request_id is not None
    uuid.UUID(str(first_request_id))
    client.get(endpoint)
    dummy_api()._add_request_id()
    second_request_id = getattr(g, "request_id", None)
    uuid.UUID(str(second_request_id))
    assert str(first_request_id) != str(second_request_id)


def test_before_request(client, dummy_api):
    def test_route_1():
        return "OK", 200

    endpoint = "/"
    query_params = dict(a="1")
    current_app.add_url_rule(endpoint, test_route_1.__name__, view_func=test_route_1)
    client.get(endpoint, query_string=query_params)
    dummy_api(api_version="1.0").before_request(name=test_route_1.__name__)
    assert getattr(g, "request_start_time", None) is not None
    assert getattr(g, "request_id", None) is not None
    assert getattr(g, "api_version", None) is not None
    assert getattr(g, "request_params", None) is not None


def test_get_item_by_id_or_not_found(
    monkeypatch,
    db_session,
    dummy_api,
    dummy_service,
    dummy_crud_model,
    dummy_crud_model_object,
):
    no_created_items = 3
    existing_id = math.ceil(no_created_items / 2)
    non_existing_id = no_created_items + 1

    # Create items
    for _i in range(no_created_items):
        item = dummy_crud_model_object()
        db_session.add(item)
    db_session.commit()

    service = dummy_service
    model = dummy_crud_model
    api = dummy_api(service=service, model=model)

    api._get_item_by_id_or_not_found(existing_id)

    # Non-existing id
    with pytest.raises(NotFoundError):
        api._get_item_by_id_or_not_found(non_existing_id)

    def raise_error(*args):
        raise TypeError

    monkeypatch.setattr("app.api.service.BaseService.get_by_id", raise_error)

    with pytest.raises(BadRequestError):
        api._get_item_by_id_or_not_found("a")


class DummySchemaValidationError(Exception):
    messages = None

    def __init__(self, **kwargs):
        self.messages = kwargs.get("messages", None)


def test_handle_validation_error(dummy_api):
    api = dummy_api()
    error_status_code = None
    error_headers = None

    # List error_messages
    error = DummySchemaValidationError(messages=["1", "2"])
    validation_error = (error, None, None)

    with pytest.raises(ValidationError):
        api._handle_validation_error(
            *validation_error,
            error_status_code=error_status_code,
            error_headers=error_headers,
        )

    # Single error_message
    error = DummySchemaValidationError(messages="1")
    validation_error = (error, None, None)

    with pytest.raises(ValidationError):
        api._handle_validation_error(
            *validation_error,
            error_status_code=error_status_code,
            error_headers=error_headers,
        )

    # Missing error.messages
    error = DummySchemaValidationError(a="1")
    validation_error = (error, None, None)

    with pytest.raises(AssertionError):
        api._handle_validation_error(
            *validation_error,
            error_status_code=error_status_code,
            error_headers=error_headers,
        )


def test_post(
    monkeypatch,
    authenticated_client,
    dummy_api,
    dummy_service,
    dummy_schema,
    dummy_crud_model_object,
):
    def test_route_1():
        return "OK", 200

    endpoint = "/"
    current_app.add_url_rule(
        endpoint, test_route_1.__name__, view_func=test_route_1, methods=["POST"]
    )

    schema = dummy_schema
    service = dummy_service
    api = dummy_api(schema=schema)

    # Happy flow
    post_body = dict(txt="foo")
    data = dict(id=1, **post_body)
    item = dummy_crud_model_object(**data)

    monkeypatch.setattr("app.api.schema.BaseSchema.load", lambda *x, **y: data)
    monkeypatch.setattr("app.api.base.BaseAPI._service", lambda *x, **y: service)
    monkeypatch.setattr("app.api.service.BaseService.create", lambda *x, **y: item)
    monkeypatch.setattr(
        "app.api.response.APIResponse.create_response", lambda *x, **y: data
    )

    response = authenticated_client.post(endpoint, json=post_body)
    assert response.status_code == 200

    response = api.post()
    assert response == data

    # Deserialization failure
    def raise_validation_error(*args):
        # Third party imports
        from marshmallow.exceptions import ValidationError as SchemaValidationError

        raise SchemaValidationError(message="foo", field_name="bar")

    monkeypatch.setattr("app.api.schema.BaseSchema.load", raise_validation_error)

    response = authenticated_client.post(endpoint, json=post_body)
    assert response.status_code == 200

    with pytest.raises(ValidationError):
        api.post()

    # Non-JSON data
    post_body = dict(txt="foo")

    response = authenticated_client.post(endpoint, data=post_body)
    assert response.status_code == 200

    with pytest.raises(BadRequestError):
        api.post()


def test_get(monkeypatch, app_context, dummy_api, dummy_schema):
    schema = dummy_schema
    api = dummy_api(schema=schema)

    id = 1
    expected_result = dict(id=id, txt="foo")

    monkeypatch.setattr("app.api.base.BaseAPI._update_params", lambda *x, **y: None)
    monkeypatch.setattr(
        "app.api.base.BaseAPI._get_item_by_id_or_not_found", lambda *x, **y: None
    )
    monkeypatch.setattr(
        "app.api.response.APIResponse.create_response", lambda *x, **y: expected_result
    )

    # Happy flow
    result = api.get(id)
    assert result == expected_result


def test_index(monkeypatch, app_context, dummy_api, dummy_schema, dummy_service):
    def test_route_1():
        return "OK", 200

    assert test_route_1() == ("OK", 200)

    endpoint = "/"
    current_app.add_url_rule(
        endpoint, test_route_1.__name__, view_func=test_route_1, methods=["GET"]
    )

    schema = dummy_schema
    service = dummy_service
    api = dummy_api(schema=schema)

    monkeypatch.setattr("app.api.base.BaseAPI._service", lambda *x, **y: service)
    monkeypatch.setattr("app.api.service.BaseService.list", lambda *x, **y: None)
    monkeypatch.setattr(
        "app.api.response.APIResponse.create_paginated_response", lambda *x, **y: None
    )

    # Unwrap the use_args() decorator
    index = api.index
    _index = inspect.unwrap(index)

    # Happy flow
    args = dict(items_per_page=5, page_index=1)

    response = _index(api, args)

    assert response is None

    # Missing page and start index
    args = dict(items_per_page=5,)

    with pytest.raises(BadRequestError):
        _index(api, args)


def test_put(
    monkeypatch,
    authenticated_client,
    dummy_api,
    dummy_service,
    dummy_schema,
    dummy_crud_model_object,
):
    def test_route_1():
        return "OK", 200

    endpoint = "/"
    current_app.add_url_rule(
        endpoint, test_route_1.__name__, view_func=test_route_1, methods=["PUT"]
    )

    schema = dummy_schema
    service = dummy_service
    api = dummy_api(schema=schema)

    # Happy flow
    put_body = dict(txt="foo")
    id = 1
    data = dict(id=id, **put_body)
    item = dummy_crud_model_object(**data)

    monkeypatch.setattr("app.api.base.BaseAPI._update_params", lambda *x, **y: None)
    monkeypatch.setattr("app.api.schema.BaseSchema.load", lambda *x, **y: data)
    monkeypatch.setattr("app.api.base.BaseAPI._service", lambda *x, **y: service)
    monkeypatch.setattr("app.api.service.BaseService.update", lambda *x, **y: item)
    monkeypatch.setattr(
        "app.api.response.APIResponse.create_response", lambda *x, **y: data
    )
    monkeypatch.setattr(
        "app.api.base.BaseAPI._get_item_by_id_or_not_found", lambda *x, **y: None
    )

    response = authenticated_client.put(endpoint, json=put_body)
    assert response.status_code == 200

    response = api.put(id)
    assert response == data

    # Deserialization failure
    def raise_validation_error(*args):
        # Third party imports
        from marshmallow.exceptions import ValidationError as SchemaValidationError

        raise SchemaValidationError(message="foo", field_name="bar")

    monkeypatch.setattr("app.api.schema.BaseSchema.load", raise_validation_error)

    response = authenticated_client.put(endpoint, json=put_body)
    assert response.status_code == 200

    with pytest.raises(ValidationError):
        api.put(id)

    # Non-JSON data
    put_body = dict(txt="foo")

    response = authenticated_client.put(endpoint, data=put_body)
    assert response.status_code == 200

    with pytest.raises(BadRequestError):
        api.put(id)


def test_delete(
    monkeypatch,
    authenticated_client,
    dummy_api,
    dummy_service,
    dummy_schema,
    dummy_crud_model,
):
    def test_route_1():
        return "OK", 200

    endpoint = "/"
    current_app.add_url_rule(
        endpoint, test_route_1.__name__, view_func=test_route_1, methods=["DELETE"]
    )

    schema = dummy_schema
    service = dummy_service
    model = dummy_crud_model
    api = dummy_api(schema=schema, model=model)

    monkeypatch.setattr("app.api.base.BaseAPI._update_params", lambda *x, **y: None)
    monkeypatch.setattr(
        "app.api.base.BaseAPI._get_item_by_id_or_not_found", lambda *x, **y: None
    )
    monkeypatch.setattr("app.api.base.BaseAPI._service", lambda *x, **y: service)
    monkeypatch.setattr("app.api.service.BaseService.delete", lambda *x, **y: None)
    monkeypatch.setattr(
        "app.api.response.APIResponse.create_success_response", lambda *x, **y: None
    )

    # Happy flow
    id = 1
    response = authenticated_client.delete(endpoint)
    assert response.status_code == 200

    api.delete(id)
