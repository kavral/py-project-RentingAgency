"""Decorators for cross-cutting behavior."""

import functools
import inspect
from datetime import datetime
from typing import Any, Callable


def log_action(func: Callable) -> Callable:
    """Decorator: log each service method call with timestamp."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[LOG {timestamp}] Calling {func.__name__}()")
        result = func(*args, **kwargs)
        return result

    return wrapper


def require_non_empty(*field_names: str) -> Callable:
    """Decorator factory: ensure named arguments are non-empty strings."""

    def decorator(func: Callable) -> Callable:
        signature = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            bound = signature.bind_partial(*args, **kwargs)
            bound.apply_defaults()
            for name in field_names:
                value = bound.arguments.get(name, "")
                if not value or not str(value).strip():
                    raise ValueError(f"Field '{name}' cannot be empty.")
            return func(*args, **kwargs)

        return wrapper

    return decorator
