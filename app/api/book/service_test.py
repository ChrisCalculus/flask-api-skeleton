# Local application imports
from app.api.book import BookService
from app.api.service import BaseService


def test_book_service(dummy_crud_model):
    book_service = BookService(model=dummy_crud_model)
    assert isinstance(book_service, BaseService)
