# Third party imports
import pytest

# Local application imports
from app.api.service import BaseService


def test_base_service(dummy_crud_model):
    base_service = BaseService(dummy_crud_model)
    assert base_service.model == dummy_crud_model


def test_get_by_id(db_session, dummy_crud_model):
    obj = dummy_crud_model(txt="foo")
    db_session.add(obj)
    db_session.commit()

    base_service = BaseService(dummy_crud_model)
    assert base_service.get_by_id(obj.id) == obj

    with pytest.raises(TypeError):
        base_service.get_by_id("a")


def test_list(monkeypatch, db_session, dummy_crud_model):
    obj = dummy_crud_model(txt="foo")
    db_session.add(obj)
    db_session.commit()

    monkeypatch.setattr("app.api.model.CRUDModelMixin.filter", lambda *x, **y: None)

    base_service = BaseService(dummy_crud_model)
    assert base_service.list() is None
    assert base_service.list([]) is None

    with pytest.raises(AssertionError):
        base_service.list("a")


def test_create(monkeypatch, dummy_crud_model):
    expected_output = None
    data = dict(txt="foo")
    monkeypatch.setattr(
        "app.api.model.CRUDModelMixin.create", lambda *x, **y: expected_output
    )
    base_service = BaseService(dummy_crud_model)
    assert base_service.create(data) == expected_output

    with pytest.raises(AssertionError):
        base_service.create("a")

    with pytest.raises(AssertionError):
        base_service.create(data, "a")


def test_update(monkeypatch, dummy_crud_model):
    item = dummy_crud_model(txt="foo")
    data = dict(txt="bar")
    expected_output = None
    monkeypatch.setattr(
        "app.api.model.CRUDModelMixin.update", lambda *x, **y: expected_output
    )
    base_service = BaseService(dummy_crud_model)
    assert base_service.update(item, data) == expected_output

    with pytest.raises(AssertionError):
        base_service.update("a", data)

    with pytest.raises(AssertionError):
        base_service.update(item, "a")

    with pytest.raises(AssertionError):
        base_service.update(item, data, "a")


def test_delete(monkeypatch, dummy_crud_model):
    item = dummy_crud_model(txt="foo")
    expected_output = None
    monkeypatch.setattr(
        "app.api.model.CRUDModelMixin.delete", lambda *x, **y: expected_output
    )
    base_service = BaseService(dummy_crud_model)
    assert base_service.delete(item) == expected_output

    with pytest.raises(AssertionError):
        base_service.delete("a")

    with pytest.raises(AssertionError):
        base_service.delete(item, "a")
