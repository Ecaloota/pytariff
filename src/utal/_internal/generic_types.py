from enum import Enum
from typing import TypeVar


class Consumption(str, Enum):
    kWh = "kWh"
    _null = "_null_consumption"


class Demand(str, Enum):
    kW = "kW"
    _null = "_null_demand"


class TradeDirection(str, Enum):
    Import = "Import"
    Export = "Export"


class SignConvention(str, Enum):
    """
    Passive convention: Load export is defined as positive
    Active convention: Load export is defined as negative
    """

    Passive = "Passive"
    Active = "Active"


MetricType = TypeVar("MetricType", Demand, Consumption)
