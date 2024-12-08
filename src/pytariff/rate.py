from __future__ import annotations

from typing import Any, Callable

from pydantic.dataclasses import dataclass
from whenever import ZonedDateTime


@dataclass
class TariffRate:
    """A TariffRate is a value (or some callable to obtain a value) in
    some registered currency."""

    currency: str  # TODO makes sense to restrict this to ISO format length
    value: float | Callable[[ZonedDateTime], float]  # TODO this should be a Decimal?

    def get_value(self, *args: Any) -> float:
        raise NotImplementedError
        # return self.value


@dataclass
class _NullRate(TariffRate):
    currency: None = None
    value: None = None
