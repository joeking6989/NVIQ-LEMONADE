from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .errors import LemonadeError


class LemonadeClient:
    def __init__(self, base_url: str = "http://127.0.0.1:13305", *, api_key: str | None = None, timeout_s: float = 60.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_s = timeout_s

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": "NVIQ-Lemonade/0.1",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _request(self, method: str, path: str, payload: dict | None = None, *, optional_404: bool = False):
        headers = self._headers()
        body = None
        if payload is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        request = Request(f"{self.base_url}{path}", data=body, headers=headers, method=method)
        try:
            with urlopen(request, timeout=self.timeout_s) as response:
                raw = response.read()
        except HTTPError as exc:
            if optional_404 and exc.code == 404:
                return None
            detail = ""
            try:
                parsed = json.loads(exc.read().decode("utf-8"))
                detail = parsed.get("error", {}).get("message", "") if isinstance(parsed, dict) else ""
            except Exception:
                detail = ""
            suffix = f": {detail}" if detail else ""
            raise LemonadeError(f"Lemonade HTTP {exc.code} for {path}{suffix}") from exc
        except URLError as exc:
            raise LemonadeError(f"Could not reach Lemonade at {self.base_url}: {exc.reason}") from exc
        except TimeoutError as exc:
            raise LemonadeError(f"Lemonade request timed out after {self.timeout_s}s: {path}") from exc

        try:
            return json.loads(raw.decode("utf-8"))
        except Exception as exc:
            raise LemonadeError(f"Lemonade returned invalid JSON for {path}") from exc

    def health(self) -> dict:
        result = self._request("GET", "/v1/health")
        if not isinstance(result, dict):
            raise LemonadeError("Lemonade /v1/health returned an invalid response")
        return result

    def models(self) -> list[dict]:
        result = self._request("GET", "/v1/models")
        if isinstance(result, dict) and isinstance(result.get("data"), list):
            return [item for item in result["data"] if isinstance(item, dict)]
        if isinstance(result, list):
            return [item for item in result if isinstance(item, dict)]
        raise LemonadeError("Lemonade /v1/models returned an invalid model list")

    def chat(self, model: str, messages: list[dict], *, temperature: float = 0.0) -> dict:
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "temperature": temperature,
        }
        result = self._request("POST", "/v1/chat/completions", payload)
        if not isinstance(result, dict):
            raise LemonadeError("Lemonade chat completion returned an invalid response")
        return result

    def stats(self) -> dict | None:
        result = self._request("GET", "/v1/stats", optional_404=True)
        return result if isinstance(result, dict) else None

    def system_info(self) -> dict | None:
        result = self._request("GET", "/v1/system-info", optional_404=True)
        return result if isinstance(result, dict) else None
