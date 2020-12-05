# Third party imports
import pytest
from sqlalchemy.exc import DataError

# Local application imports
from app.api.model import CRUDModelMixin, Model


def test_model():
    model = Model()
    assert isinstance(model, Model)


def test_crud_model_mixin_find(db_session, dummy_crud_model):
    assert issubclass(dummy_crud_model, CRUDModelMixin)

    obj_1 = dummy_crud_model(txt="obj_1")
    obj_2 = dummy_crud_model(txt="obj_2")

    db_session.add(obj_1)
    db_session.add(obj_2)

    find = dummy_crud_model.find(txt="obj_1")
    assert find is not None
    assert find.txt == obj_1.txt


def test_crud_model_mixin_find_or_create(db_session, dummy_crud_model):
    assert issubclass(dummy_crud_model, CRUDModelMixin)

    obj_1 = dummy_crud_model(txt="obj_1")
    obj_2 = dummy_crud_model(txt="obj_2")

    db_session.add(obj_1)
    db_session.add(obj_2)

    find_or_create = dummy_crud_model.find_or_create(txt="obj_3")
    assert find_or_create is not None
    assert find_or_create.txt == "obj_3"
    assert len(dummy_crud_model.query.all()) == 3


def test_crud_model_mixin_get_by_id(db_session, dummy_crud_model):
    assert issubclass(dummy_crud_model, CRUDModelMixin)

    obj_1 = dummy_crud_model(txt="obj_1")
    obj_2 = dummy_crud_model(txt="obj_2")

    db_session.add(obj_1)
    db_session.add(obj_2)

    get_by_id = dummy_crud_model.get_by_id(1)
    assert get_by_id.txt == obj_1.txt

    with pytest.raises(TypeError):
        dummy_crud_model.get_by_id("a")


def test_crud_model_mixin_filter(db_session, dummy_crud_model):
    assert issubclass(dummy_crud_model, CRUDModelMixin)

    obj_1 = dummy_crud_model(txt="obj_1")
    obj_2 = dummy_crud_model(txt="obj_2")
    obj_3 = dummy_crud_model(txt="obj_3")

    db_session.add(obj_1)
    db_session.add(obj_2)
    db_session.add(obj_3)

    equal_filter = [("txt", "eq", "obj_1")]
    equal = dummy_crud_model.filter(equal_filter)
    assert equal is not None
    assert len(equal.all()) == 1
    assert equal.first().txt == obj_1.txt

    lt_filter = [("id", "lt", 2)]
    lt = dummy_crud_model.filter(lt_filter)
    assert lt is not None
    assert len(lt.all()) == 1
    assert lt.first().txt == obj_1.txt

    gt_filter = [("id", "gt", 2)]
    gt = dummy_crud_model.filter(gt_filter)
    assert gt is not None
    assert len(gt.all()) == 1
    assert [x.txt for x in gt.all()].sort() == [obj_3.txt].sort()

    le_filter = [("id", "le", 2)]
    le = dummy_crud_model.filter(le_filter)
    assert le is not None
    assert len(le.all()) == 2
    assert [x.txt for x in le.all()].sort() == [obj_1.txt, obj_2.txt].sort()

    ge_filter = [("id", "ge", 2)]
    ge = dummy_crud_model.filter(ge_filter)
    assert ge is not None
    assert len(ge.all()) == 2
    assert [x.txt for x in gt.all()].sort() == [obj_2.txt, obj_3.txt].sort()

    in_filter = [("id", "in", [1, 2])]
    _in = dummy_crud_model.filter(in_filter)
    assert _in is not None
    assert len(_in.all()) == 2
    assert [x.txt for x in _in.all()].sort() == [obj_1.txt, obj_2.txt].sort()

    in_str_filter = [("txt", "in", "obj_1,obj_2")]
    _in_str = dummy_crud_model.filter(in_str_filter)
    assert _in_str is not None
    assert len(_in_str.all()) == 2
    assert [x.txt for x in _in_str.all()].sort() == [obj_1.txt, obj_2.txt].sort()

    like_filter = [("txt", "like", "%_1%")]
    like = dummy_crud_model.filter(like_filter)
    assert len(like.all()) == 1
    assert like.first().txt == obj_1.txt

    combined_filter = lt_filter + equal_filter
    combined = dummy_crud_model.filter(combined_filter)
    assert len(combined.all()) == 1
    assert combined.first().txt == obj_1.txt

    null_obj = dummy_crud_model(txt=None)
    db_session.add(null_obj)
    null_filter = [("txt", "eq", "null")]
    null = dummy_crud_model.filter(null_filter)
    assert len(null.all()) == 1
    assert null.first().txt is None

    with pytest.raises(TypeError):
        dummy_crud_model.filter("a")

    with pytest.raises(TypeError):
        dummy_crud_model.filter([equal_filter])

    with pytest.raises(TypeError):
        dummy_crud_model.filter(["a", "b"])

    with pytest.raises(ValueError):
        dummy_crud_model.filter([("a", "lt")])

    with pytest.raises(DataError):
        invalid_lt_filter = [("id", "lt", "a")]
        dummy_crud_model.filter(invalid_lt_filter).all()

    with pytest.raises(ValueError):
        non_existing_column_filter = [("id1", "lt", 2)]
        dummy_crud_model.filter(non_existing_column_filter).all()

    with pytest.raises(ValueError):
        invalid_filter = [("id", "foo", 2)]
        dummy_crud_model.filter(invalid_filter).all()


def test_crud_model_mixin_create(db_session, dummy_crud_model):
    assert issubclass(dummy_crud_model, CRUDModelMixin)

    create = dummy_crud_model(session=db_session).create(txt="obj_4")
    assert create is not None
    assert create.txt == "obj_4"


def test_crud_model_mixin_update(db_session, dummy_crud_model):
    assert issubclass(dummy_crud_model, CRUDModelMixin)

    obj_1 = dummy_crud_model(txt="obj_1")
    db_session.add(obj_1)
    db_session.commit()

    obj_1.update(txt="obj_1a")

    assert dummy_crud_model.query.first().txt == "obj_1a"

    with pytest.raises(AssertionError):
        obj_1.update(txt1="obj_1a")


def test_crud_model_mixin_save(db_session, dummy_crud_model):
    assert issubclass(dummy_crud_model, CRUDModelMixin)
    obj = dummy_crud_model(session=db_session, txt="obj")
    obj.save()


def test_crud_model_mixin_delete(db_session, dummy_crud_model):
    assert issubclass(dummy_crud_model, CRUDModelMixin)
    obj = dummy_crud_model.create(session=db_session, txt="obj")
    assert len(dummy_crud_model.query.all()) == 1
    obj.delete()
    assert len(dummy_crud_model.query.all()) == 0
