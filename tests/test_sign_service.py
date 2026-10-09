import pytest

from src.sign_service import ContractRequest, ReleaseResult, release_contract


class FakeClient:
    def generate(self, markdown):
        assert "contract-42" in markdown
        return {"download_url": "https://files.example/contract-42.pdf"}


def test_release_emits_business_event():
    request = ContractRequest("contract-42", ("Acme", "Dev Team"), "Terms apply.")
    result = release_contract(request, FakeClient())
    assert isinstance(result, ReleaseResult)
    assert result.event == "contract.pdf_generated"


def test_rate_limit_retries(monkeypatch):
    from src.sign_service import InfraiPdfClient

    class Response:
        def __init__(self, status, body):
            self.status_code, self.body, self.headers = status, body, {}

        def json(self):
            return self.body

    class Session:
        def __init__(self):
            self.responses = iter([Response(429, {"ok": False, "error": {"code": "RATE_LIMITED"}}), Response(200, {"ok": True, "data": {"id": "pdf-1"}})])

        def request(self, *args, **kwargs):
            return next(self.responses)

    monkeypatch.setattr("src.sign_service.time.sleep", lambda _: None)
    assert InfraiPdfClient("test", Session()).generate("hello") == {"id": "pdf-1"}
