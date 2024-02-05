from enum import Enum
from typing import Generic, Literal

from pydantic.dataclasses import dataclass
from pytariff.core.typing import Consumption, Demand, MetricType


class TradeDirection(str, Enum):
    Import = "Import"
    Export = "Export"
    _null = "_null_direction"  # when providing meter profiles, nonsensical to provide import/export


class SignConvention(str, Enum):
    """
    Passive convention: Load export is defined as positive
    Active convention: Load export is defined as negative
    """

    Passive = "Passive"
    Active = "Active"

    def _import_sign(self) -> Literal[-1, 1]:
        return -1 if self == SignConvention.Passive else 1

    def _export_sign(self) -> Literal[-1, 1]:
        return -1 if self == SignConvention.Active else 1

    def _is_export(self, value: float) -> bool:
        is_passive_export = self == SignConvention.Passive and value > 0
        is_active_export = self == SignConvention.Active and value < 0
        print
        return is_passive_export or is_active_export

    def _is_import(self, value: float) -> bool:
        is_passive_import = self == SignConvention.Passive and value < 0
        is_active_import = self == SignConvention.Active and value > 0
        return is_passive_import or is_active_import


class UsageChargeMethod(Enum):
    """Defines how the TariffUnit provided in a TariffCharge definition is to be charged"""

    mean = "mean"
    max = "max"
    rolling_mean = "rolling_mean"
    cumsum = "cumsum"
    identity = "identity"  # i.e. apply identity to usage values in meter profile


@dataclass
class TariffUnit(Generic[MetricType]):
    metric: MetricType
    convention: SignConvention
    direction: TradeDirection | None = None

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
