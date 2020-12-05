# Third party imports
import pytest

# Local application imports
from app.api.representation import output_json


def test_output_json(app_context, monkeypatch):
    monkeypatch.setattr("app.api.representation.make_response", lambda *x: None)

    # Happy flow
    data = {}
    code = 200
    headers = None
    response = output_json(data, code, headers)
    assert response is None

    # Headers
    data = {}
    code = 200
    headers = {"x-header": "a"}
    response = output_json(data, code, headers)
    assert response is None

    with pytest.raises(AssertionError):
        output_json({}, "a")

    with pytest.raises(AssertionError):
        output_json(None, 200)

    with pytest.raises(AssertionError):
        output_json({}, 200, "a")
