# Local application imports
from app.api.model import CRUDModelMixin, Model
from app.extensions import db


class Book(CRUDModelMixin, Model):

    __tablename__ = "book"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False)

    def __str__(self):
        return self.title

    @classmethod
    def seed(cls, fake):
        book = Book(
            title=fake.sentence(),
        )
        book.save()
