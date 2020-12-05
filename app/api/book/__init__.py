# Local application imports
from app.api.base import BaseAPI

# Local folder imports
from .model import Book
from .schema import BookSchema
from .service import BookService


class BookAPI(BaseAPI):
    model = Book
    route_base = "book"
    schema = BookSchema
    api_version = "1.0"
    service = BookService
