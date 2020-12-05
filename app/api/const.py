# Standard library imports
from enum import Enum

# Local application imports
from app.utils import localize_text

DEFAULT_ITEMS_PER_PAGE = 10


class HttpMethodVerbs(Enum):
    GET = ["retrieve", "retrieved", "retrieving"]
    POST = ["create", "created", "creating"]
    PUT = ["update", "updated", "updating"]
    PATCH = ["update", "updated", "updating"]
    DELETE = ["delete", "deleted", "deleting"]

    def do(self):
        return localize_text(self.value[0])

    def done(self):
        return localize_text(self.value[1])

    def doing(self):
        return localize_text(self.value[2])
