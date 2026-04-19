"""Minimal TestClient to exercise the FastAPI shim."""
from __future__ import annotations

from typing import Any, Dict


class Response:
    def __init__(self, status_code: int, data: Any):
        self.status_code = status_code
        self._data = data

    def json(self) -> Any:
        return self._data


class TestClient:
    def __init__(self, app):
        self.app = app

    def get(self, path: str, json: Dict[str, Any] | None = None):
        status, data = self.app.handle_request("GET", path, json_body=json)
        return Response(status, data)

    def post(self, path: str, json: Dict[str, Any] | None = None):
        status, data = self.app.handle_request("POST", path, json_body=json)
        return Response(status, data)
