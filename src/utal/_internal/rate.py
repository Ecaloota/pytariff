from abc import ABC
from typing import Generic

from pydantic.dataclasses import dataclass

from utal._internal.generic_types import MetricType
from utal._internal.unit import RateCurrency


@dataclass
class TariffRate(ABC, Generic[MetricType]):
    """A rate is a value in some registered currency. It has no meaning independent of a parent
    TariffBlock.unit

    Not to be used directly
    """

    currency: RateCurrency
    value: float

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TariffRate):
            raise ValueError
        return self.currency == other.currency and self.value == other.value
