from abc import ABC
from datetime import datetime
from enum import Enum
from typing import Generic, Literal

from pydantic.dataclasses import dataclass
from utal._internal.generic_types import Consumption, Demand, MetricType, TradeDirection, SignConvention


class UsageChargeMethod(Enum):
    """Defines how the TariffUnit provided in a TariffCharge definition is to be charged"""

    mean = "mean"
    peak = "peak"
    rolling_mean = "rolling_mean"
    cumsum = "cumsum"


@dataclass
class TariffUnit(ABC, Generic[MetricType]):
    metric: MetricType
    direction: TradeDirection
    convention: SignConvention

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TariffUnit):
            raise ValueError
        return self.metric == other.metric and self.direction == other.direction

    def __hash__(self) -> int:
        return hash(self.metric) ^ hash(self.direction) ^ hash(self.convention)


@dataclass
class ConsumptionUnit(TariffUnit[Consumption]):
    metric: Literal[Consumption.kWh, Consumption._null]


@dataclass
class DemandUnit(TariffUnit[Demand]):
    metric: Literal[Demand.kW, Demand._null]


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


class BillingPeriod(Enum):
    DAILY = "1D"
    WEEKLY = "7D"
    FIRST_OF_MONTH = "_null_first_of_month"
    FIRST_OF_QUARTER = "_null_first_of_quarter"

    def _is_day_suffix(self) -> bool:
        return self.name in ["DAILY", "WEEKLY", "FIRST_OF_MONTH", "FIRST_OF_QUARTER"]

    def _to_days(self, _from: datetime) -> str:
        """Convert the ResetPeriod to some number of days, required when using reset periods of
        MONTHLY, QUARTERLY, ANNUALLY. Dates are exclusive.

        NOTE same as ResetPeriod method of same name, TODO consolidate
        """

        if self.name == "FIRST_OF_MONTH":
            next_first_of_month = _from.replace(month=_from.month + 1, day=1)
            return str((next_first_of_month - _from).days) + "D"

        elif self.name == "FIRST_OF_QUARTER":
            # next quarter occurs in one of Jan, Apr, Jul, or Oct
            next_first_of_quarter = _from.replace(month=(_from.month - 1) // 3 * 3 + 4, day=1)
            return str((next_first_of_quarter - _from).days) + "D"

        # add more logic here for more BillingPeriods

        else:
            return self.value


@dataclass
class BillingData:
    start: datetime
    frequency: BillingPeriod = BillingPeriod.FIRST_OF_MONTH  # default 1/month
