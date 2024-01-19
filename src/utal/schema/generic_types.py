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


MetricType = TypeVar("MetricType", Demand, Consumption)
