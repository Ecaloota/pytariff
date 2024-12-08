from enum import Enum
from typing import Literal


class TradeDirection(str, Enum):
    Import = "Import"
    Export = "Export"


class Metric(str, Enum):
    Consumption = "Consumption"
    Demand = "Demand"


class SignConvention(str, Enum):
    """
    Passive convention: Load export is defined as positive
    Active convention: Load export is defined as negative
    """

    Passive = "Passive"
    Active = "Active"

    # TODO is this a property?
    def _import_sign(self) -> Literal[-1, 1]:
        return -1 if self == SignConvention.Passive else 1

    # TODO is this a property?
    def _export_sign(self) -> Literal[-1, 1]:
        return -1 if self == SignConvention.Active else 1

    def _is_export(self, value: float) -> bool:
        is_passive_export = self == SignConvention.Passive and value > 0
        is_active_export = self == SignConvention.Active and value < 0
        return is_passive_export or is_active_export

    def _is_import(self, value: float) -> bool:
        is_passive_import = self == SignConvention.Passive and value < 0
        is_active_import = self == SignConvention.Active and value > 0
        return is_passive_import or is_active_import
