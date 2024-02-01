from datetime import datetime
from enum import Enum
from typing import Any
from pydantic.dataclasses import dataclass


# TODO probably not required to have this
class RateCurrency(Enum):
    AUD = ("$", "AUD")
    _null = ("_null", "_null")  # for internal use only

    def __init__(self, symbol: str, iso: str) -> None:
        self._symbol = symbol
        self._iso = iso

    def __repr__(self) -> str:
        return self._iso + ":" + self._symbol

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def sign(self) -> str:
        return self._symbol

    @property
    def iso(self) -> str:
        return self._iso


@dataclass
class TariffRate:
    """A rate is a value in some registered currency. It has no meaning independent of a parent
    TariffBlock.unit
    """

    currency: RateCurrency
    value: float

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TariffRate):
            raise ValueError
        return self.currency == other.currency and self.value == other.value

    def __hash__(self) -> int:
        return hash(self.currency) ^ hash(self.value)

    def get_value(self, *args: Any) -> float:
        return self.value


# TODO test this
@dataclass
class MarketRate:
    """A MarketRate is a TariffRate defined with a default currency of _null and a value
    of None. The value of a MarketRate tariff is determined on-the-fly when applied to
    MeterData.
    """

    rate_lookup: dict[datetime, float]
    currency: RateCurrency = RateCurrency._null
    value: float | None = None

    def get_value(self, t: datetime) -> float:
        # TODO
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MarketRate):
            raise ValueError
        return self.currency == other.currency and self.value == other.value

    def __hash__(self) -> int:
        return hash(self.currency) ^ hash(self.value)
