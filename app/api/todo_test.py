# Local application imports
from app.api import BookAPI
from app.api.base import BaseAPI


def test_book_api():
    book_api = BookAPI()
    assert isinstance(book_api, BookAPI)
