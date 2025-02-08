from __future__ import annotations

from typing import Any, Callable


class TariffRate:
    """A TariffRate is a value (or some callable to obtain a value) in
    some registered currency."""

    def __init__(
        self, currency: str | None, value: float | Callable[..., float]
    ) -> None:
        self.currency = currency
        self._value = value

    @property
    def value(self) -> None:
        raise AttributeError(
            "TariffRate values are accessible through the .get_value method"
        )

    def get_value(self, *args: Any, **kwargs: dict[Any, Any]) -> float:
        if callable(self._value):
            return self._value(*args, **kwargs)
        return self._value
