# Third party imports
from marshmallow import fields

# Local application imports
from app.api.schema import BaseSchema


class BookSchema(BaseSchema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
