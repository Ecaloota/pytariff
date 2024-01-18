from abc import ABC
from enum import Enum
from typing import Generic, Literal

from pydantic.dataclasses import dataclass
from utal.schema.generic_types import Consumption, Demand, MetricType, TradeDirection


@dataclass
class TariffUnit(ABC, Generic[MetricType]):
    metric: MetricType
    direction: TradeDirection


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
