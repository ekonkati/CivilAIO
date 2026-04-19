"""Minimal Pydantic-like shim used for offline testing.

This provides enough surface area for the CivilAIO mocked pipeline and tests
without requiring external dependencies. It is intentionally small and does
not attempt full validation semantics.
"""
from __future__ import annotations

from typing import Any, Callable, Dict


class Missing:
    pass


MISSING = Missing()


class FieldInfo:
    def __init__(self, default: Any = MISSING, default_factory: Callable | None = None, **_: Any):
        self.default = default
        self.default_factory = default_factory


def Field(default: Any = MISSING, default_factory: Callable | None = None, **kwargs: Any):
    return FieldInfo(default=default, default_factory=default_factory, **kwargs)


class BaseModelMeta(type):
    def __new__(mcls, name, bases, namespace):
        validators: Dict[str, list] = {}
        for attr, value in namespace.items():
            if callable(value) and hasattr(value, "__validator_fields__"):
                for field in value.__validator_fields__:
                    validators.setdefault(field, []).append(value)
        namespace["__validators__"] = validators
        return super().__new__(mcls, name, bases, namespace)


class BaseModel(metaclass=BaseModelMeta):
    __validators__: Dict[str, list]

    def __init__(self, **data: Any):
        cls = self.__class__
        annotations = getattr(cls, "__annotations__", {})
        for name in annotations:
            if name in data:
                value = data[name]
            else:
                default = getattr(cls, name, MISSING)
                if isinstance(default, FieldInfo):
                    if default.default_factory is not None:
                        value = default.default_factory()
                    elif default.default is not MISSING:
                        value = default.default
                    else:
                        raise ValueError(f"Missing required field: {name}")
                elif default is not MISSING:
                    value = default
                else:
                    value = None
            for validator_func in self.__validators__.get(name, []):
                value = validator_func(cls, value)
            setattr(self, name, value)

    def dict(self, exclude: set | None = None) -> Dict[str, Any]:
        exclude = exclude or set()
        result: Dict[str, Any] = {}
        annotations = getattr(self.__class__, "__annotations__", {})
        for name in annotations:
            if name in exclude:
                continue
            value = getattr(self, name, None)
            if isinstance(value, BaseModel):
                result[name] = value.dict()
            elif isinstance(value, list):
                result[name] = [item.dict() if isinstance(item, BaseModel) else item for item in value]
            else:
                result[name] = value
        return result

    def __repr__(self):
        return f"{self.__class__.__name__}({self.dict()})"


class BaseSettings(BaseModel):
    class Config:
        env_prefix = ""
        case_sensitive = False
        env_file = None
        env_file_encoding = "utf-8"


def validator(*fields: str, pre: bool | None = None):
    def decorator(func: Callable):
        func.__validator_fields__ = fields
        func.__validator_pre__ = pre
        return func

    return decorator


__all__ = ["BaseModel", "BaseSettings", "Field", "validator"]
