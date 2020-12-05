# Local application imports
from app.api.book import BookAPI


def register_apis(app):
    BookAPI.register(app)
