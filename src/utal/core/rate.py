from datetime import datetime
from typing import Any
from pydantic.dataclasses import dataclass


@dataclass
class TariffRate:
    """A rate is a value in some registered currency. It has no meaning independent of a parent
    TariffBlock.unit
    """

    currency: str  # TODO makes sense to restrict this to ISO format length
    value: float  # TODO this should be a Decimal?

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
    currency: str  # TODO makes sense to restrict this to ISO format length
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
