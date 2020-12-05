# Local application imports
from app.api.const import HttpMethodVerbs


def test_http_method_verbs(monkeypatch):
    def _return(val):
        return val

    monkeypatch.setattr("app.api.const.localize_text", _return)

    assert [len(v.value) == 3 for v in HttpMethodVerbs]

    assert HttpMethodVerbs.GET.do() == HttpMethodVerbs.GET.value[0]
    assert HttpMethodVerbs.GET.done() == HttpMethodVerbs.GET.value[1]
    assert HttpMethodVerbs.GET.doing() == HttpMethodVerbs.GET.value[2]
