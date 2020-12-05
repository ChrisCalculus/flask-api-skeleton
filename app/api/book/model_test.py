# Local application imports
from app.api.book import Book


def test_book(db_session, app_context):
    book = Book.create(title="foo")
    assert str(book) == book.title


class DummyFaker:
    @staticmethod
    def sentence():
        return "lipsum"

    @staticmethod
    def random_int(*args, **kwargs):
        return 1


def test_book_seed(monkeypatch):
    def save(self):
        return self

    monkeypatch.setattr("app.api.model.CRUDModelMixin.save", save)
    dummy_faker = DummyFaker()
    Book.seed(dummy_faker)
