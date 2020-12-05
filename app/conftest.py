# Third party imports
import pytest

# Local application imports
from app.api.base import BaseAPI
from app.api.model import CRUDModelMixin, Model
from app.api.schema import BaseSchema
from app.extensions import db as _db


@pytest.fixture
def app():
    # Local application imports
    from app import create_app
    from app.config import TestConfig

    config = TestConfig

    return create_app(config=config)


@pytest.fixture
def app_context(app):
    """ Creates a flask app context containing: current_app, g. """
    with app.app_context():
        yield app


# @pytest.fixture
# def request_context(app_context):
#     """ Creates a flask request context containing: session, request. """
#     with app_context.test_request_context():
#         yield


@pytest.fixture
def client(app_context):
    with app_context.test_client(use_cookies=True) as client:
        # Keep the context available in the test function
        yield client


@pytest.yield_fixture
def db(app):
    """ Creates a fresh db for testing. """
    with app.app_context():
        _db.drop_all()
        _db.create_all()
        yield _db
        _db.drop_all()
        _db.session.commit()


@pytest.yield_fixture
def db_session(db):
    """ Creates a transactional context for tests to run in. """
    connection = db.engine.connect()
    transaction = connection.begin()
    options = dict(bind=connection, binds={})
    scoped_session = db.create_scoped_session(options=options)
    db.session = scoped_session
    yield scoped_session
    transaction.rollback()
    connection.close()
    scoped_session.remove()


@pytest.fixture
def authenticated_client(client, db_session):
    # TODO: Create user
    db_session.commit()
    # TODO: Authenticate
    return client


class DummyModel(Model):
    __tablename__ = "dummy_model"
    __table_args__ = {"extend_existing": True}
    id = _db.Column(_db.Integer, primary_key=True)


@pytest.fixture
def dummy_model():
    # Local application imports
    return DummyModel


@pytest.fixture
def dummy_model_object(dummy_model):
    def _dummy_model_object():
        return dummy_model()

    return _dummy_model_object


class DummyCRUDModel(CRUDModelMixin, Model):
    __tablename__ = "dummy_crud_model"
    __table_args__ = {"extend_existing": True}
    id = _db.Column(_db.Integer, primary_key=True)
    txt = _db.Column(_db.String, nullable=True)


@pytest.fixture
def dummy_crud_model():
    return DummyCRUDModel


@pytest.fixture
def dummy_crud_model_object(dummy_crud_model):
    def _dummy_crud_model_object(**kwargs):
        return dummy_crud_model(**kwargs)

    return _dummy_crud_model_object


@pytest.fixture
def dummy_service(dummy_model):
    # Local application imports
    from app.api.service import BaseService

    class DummyService(BaseService):
        model = dummy_model

    return DummyService


@pytest.fixture
def dummy_service_object():
    # Local application imports
    from app.api.service import BaseService

    class DummyService(BaseService):
        def __init__(self, *args, **kwargs):
            self.__dict__.update(kwargs)

    def _dummy_service(**kwargs):
        return DummyService(**kwargs)

    return _dummy_service


class DummyAPI(BaseAPI):
    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def dummy_api():
    def _dummy_api(**kwargs):
        return DummyAPI(**kwargs)

    return _dummy_api


class DummySchema(BaseSchema):
    pass


@pytest.fixture
def dummy_schema():
    return DummySchema
