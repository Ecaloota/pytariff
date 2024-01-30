from abc import ABC
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
