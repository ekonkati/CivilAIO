"""Lightweight FastAPI shim for offline testing.

This module provides minimal stand-ins for FastAPI classes so the mock
CivilAIO service can be exercised without external dependencies. It is
*not* a full implementation of FastAPI and only supports the behaviours
used in the tests.
"""
from __future__ import annotations

import inspect
from typing import Any, Callable, Dict, List, Optional, Tuple


class HTTPException(Exception):
    def __init__(self, status_code: int, detail: str | None = None):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail or ""


class Route:
    def __init__(self, method: str, path: str, handler: Callable, status_code: int = 200):
        self.method = method.upper()
        self.path = path
        self.handler = handler
        self.status_code = status_code


class APIRouter:
    def __init__(self):
        self.routes: List[Route] = []

    def _register(self, method: str, path: str, status_code: int):
        def decorator(func: Callable):
            self.routes.append(Route(method, path, func, status_code=status_code))
            return func

        return decorator

    def get(self, path: str, response_model=None, tags=None, status_code: int = 200):
        return self._register("GET", path, status_code)

    def post(self, path: str, response_model=None, tags=None, status_code: int = 200):
        return self._register("POST", path, status_code)


class FastAPI:
    def __init__(self, title: str = "FastAPI", version: str = "0.0.0"):
        self.title = title
        self.version = version
        self.routes: List[Route] = []
        self.middleware_stack: List[Any] = []

    def add_middleware(self, middleware_class, **options):
        # Middleware is not executed in the shim but recorded for parity.
        self.middleware_stack.append((middleware_class, options))

    def include_router(self, router: APIRouter, prefix: str = ""):
        for route in router.routes:
            full_path = (prefix.rstrip("/") + route.path) or "/"
            self.routes.append(Route(route.method, full_path, route.handler, route.status_code))

    def _register(self, method: str, path: str):
        def decorator(func: Callable):
            self.routes.append(Route(method, path, func, status_code=200))
            return func

        return decorator

    def get(self, path: str, response_model=None, tags=None):
        return self._register("GET", path)

    def post(self, path: str, response_model=None, tags=None, status_code: int = 200):
        def decorator(func: Callable):
            self.routes.append(Route("POST", path, func, status_code=status_code))
            return func

        return decorator

    # The TestClient defined in fastapi.testclient calls this to execute handlers.
    def handle_request(self, method: str, path: str, json_body: Optional[dict] = None):
        json_body = json_body or {}
        method = method.upper()
        for route in self.routes:
            matched, params = _match_path(route.path, path)
            if matched and route.method == method:
                try:
                    result = _invoke(route.handler, params, json_body)
                    payload = _to_plain(result)
                    return route.status_code, payload
                except HTTPException as exc:  # noqa: PERF203 - narrow scope
                    return exc.status_code, {"detail": exc.detail}
        return 404, {"detail": "Not Found"}


def _invoke(handler: Callable, path_params: Dict[str, str], body: Dict[str, Any]):
    sig = inspect.signature(handler)
    bound_args = {}
    for name, param in sig.parameters.items():
        if name in path_params:
            bound_args[name] = path_params[name]
        elif param.annotation != inspect.Parameter.empty:
            model = param.annotation
            if isinstance(model, str):
                model = handler.__globals__.get(model, model)
            try:
                bound_args[name] = model(**body)  # type: ignore[arg-type]
            except Exception:
                bound_args[name] = body
        else:
            bound_args[name] = body
    result = handler(**bound_args)
    if inspect.iscoroutine(result):
        # Run async handlers synchronously for the shim.
        import asyncio

        return asyncio.get_event_loop().run_until_complete(result)
    return result


def _match_path(template: str, path: str) -> Tuple[bool, Dict[str, str]]:
    t_parts = [part for part in template.split("/") if part]
    p_parts = [part for part in path.split("/") if part]
    if len(t_parts) != len(p_parts):
        return False, {}
    params: Dict[str, str] = {}
    for t, p in zip(t_parts, p_parts):
        if t.startswith("{") and t.endswith("}"):
            params[t.strip("{} ")] = p
        elif t != p:
            return False, {}
    return True, params


def _to_plain(obj: Any):
    if hasattr(obj, "dict"):
        return obj.dict()
    if isinstance(obj, list):
        return [_to_plain(item) for item in obj]
    return obj


# Convenience imports for compatibility with from fastapi import APIRouter, HTTPException
__all__ = ["APIRouter", "FastAPI", "HTTPException"]
