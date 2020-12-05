# Standard library imports
from typing import List, Optional

# Local application imports
from app.error import BaseError
from app.utils import localize_text


class APIError(BaseError):
    code: Optional[int] = None
    message: Optional[str] = None
    errors: Optional[List[dict]] = None

    def __init__(self, errors: List[dict] = None, **kwargs):
        self.errors = errors


class BadRequestError(APIError):
    code = 400

    def __init__(self, message=None, **kwargs):
        super().__init__(**kwargs)
        self.message = message or localize_text("error_bad_request")


class NotFoundError(APIError):
    code = 404

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = localize_text("error_not_found")


class ValidationError(APIError):
    code = 422

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message = localize_text("error_validation")
