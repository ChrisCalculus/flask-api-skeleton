# Standard library imports
from datetime import datetime as dt

# Third party imports
from flask import g
from marshmallow import fields
from marshmallow.schema import BaseSchema as Schema

# Local application imports
from app.utils import camelcase, timedelta_in_ms


class BaseSchema(Schema):
    def on_bind_field(self, field_name, field_obj):
        """Automatically camelcase keys in the response object"""
        field_obj.data_key = camelcase(field_obj.data_key or field_name)


class APIPaginationDataSchema(BaseSchema):
    items_per_page = fields.Int()
    current_item_count = fields.Int(dump_only=True)
    page_index = fields.Int()
    start_index = fields.Int()
    total_items = fields.Int(dump_only=True)
    total_pages = fields.Int(dump_only=True)
    items = fields.List(fields.Raw(), dump_only=True)


class APIMessageSchema(BaseSchema):
    message = fields.String()


class APIErrorSchema(APIMessageSchema):
    code = fields.Integer()
    errors = fields.Raw()


class APIResponseSchema(BaseSchema):
    """Inspiration: https://google.github.io/styleguide/jsoncstyleguide.xml"""

    api_version = fields.String()
    id = fields.String()
    params = fields.Dict(keys=fields.Str(), values=fields.Raw())
    duration = fields.Function(
        lambda _: timedelta_in_ms(dt.now(), getattr(g, "request_start_time", None))
    )


class APISingleResponseSchema(APIResponseSchema):
    """Inspiration: https://google.github.io/styleguide/jsoncstyleguide.xml"""

    data = fields.Raw()


class APIPaginatedResponseSchema(APIResponseSchema):
    """Inspiration: https://google.github.io/styleguide/jsoncstyleguide.xml"""

    data = fields.Nested(APIPaginationDataSchema)


class APIErrorResponseSchema(APIResponseSchema):
    """Inspiration: https://google.github.io/styleguide/jsoncstyleguide.xml"""

    error = fields.Nested(APIErrorSchema)


class APISuccessResponseSchema(APIResponseSchema):
    success = fields.Nested(APIMessageSchema)
