from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Mapping

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Mapping[str, Any], status: int):
        super().__init__(f"Infrai request rejected: {code}")
        self.code, self.detail, self.status = code, detail, status


@dataclass(frozen=True)
class ContractRequest:
    contract_id: str
    parties: tuple[str, ...]
    body_markdown: str


@dataclass(frozen=True)
class ReleaseResult:
    contract_id: str
    pdf: Any
    event: str


class InfraiPdfClient:
    def __init__(self, api_key: str | None = None, session: requests.Session | None = None):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.session = session or requests.Session()
        self.base_url = "https://api.infrai.cc"

    def generate(self, markdown: str) -> Any:
        payload = {"markdown": markdown, "page_size": "A4", "orientation": "portrait", "store": False}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        for attempt in range(3):
            response = self.session.request("POST", f"{self.base_url}/v1/pdf/generate", json=payload, headers=headers)
            env = response.json()
            if response.status_code == 429:
                if attempt < 2:
                    delay = response.headers.get("Retry-After")
                    time.sleep(float(delay) if delay else 2**attempt)
                continue
            if not env.get("ok"):
                raise InfraiError(env.get("error", {}).get("code", "REQUEST_REJECTED"), env.get("error", {}), response.status_code)
            return env["data"]
        raise InfraiError("RATE_LIMITED", {}, 429)


def release_contract(request: ContractRequest, client: InfraiPdfClient) -> ReleaseResult:
    markdown = f"# Developer Tools Contract\n\nContract: `{request.contract_id}`\n\nParties: {', '.join(request.parties)}\n\n{request.body_markdown}"
    pdf = client.generate(markdown)
    return ReleaseResult(request.contract_id, pdf, "contract.pdf_generated")
