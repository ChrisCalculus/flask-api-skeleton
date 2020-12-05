# Standard library imports
from typing import Optional

# Third party imports
from sqlalchemy.orm import Query

# Local folder imports
from .model import CRUDModelMixin, Model


class BaseService:
    model = None

    def __init__(self, model):
        assert model is not None and issubclass(model, CRUDModelMixin)
        self.model = model

    def get_by_id(self, id: int) -> Optional[Model]:
        if not isinstance(id, int):
            raise TypeError
        assert self.model is not None
        return self.model.get_by_id(id)

    def list(self, filters=None) -> Query:
        filters = filters or []
        assert isinstance(filters, list)
        assert self.model is not None
        return self.model.filter(filters)

    def create(self, data: dict, commit: bool = True) -> Model:
        assert isinstance(commit, bool)
        assert isinstance(data, dict)
        assert self.model is not None
        return self.model.create(commit, **data)

    @staticmethod
    def update(item: Model, data: dict, commit: bool = True) -> Model:
        assert isinstance(commit, bool)
        assert isinstance(item, Model)
        assert isinstance(data, dict)
        return item.update(commit, **data)

    @staticmethod
    def delete(item: Model, commit: bool = True):
        assert isinstance(item, Model)
        assert isinstance(commit, bool)
        item.delete(commit=commit)
        return
