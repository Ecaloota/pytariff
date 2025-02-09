from enum import Enum
from typing import Literal


class TradeDirection(str, Enum):
    """The direction of power flow.
    'Import' is from generator to load;
    'Export' is from load to generator."""

    Import = "Import"
    Export = "Export"


class Metric(str, Enum):
    """The metric of power flow being considered.
    'Consumption' is power over time;
    'Demand' is power demand;
    """

    Consumption = "Consumption"
    Demand = "Demand"


class SignConvention(str, Enum):
    """
    Passive convention: Load export is defined as positive
    Active convention: Load export is defined as negative
    """

    Passive = "Passive"
    Active = "Active"

    @property
    def import_factor(self) -> Literal[-1, 1]:
        """A constant factor which determines the sign of a quantity
        imported under either the Passive or Active SignConvention;
        (a) 1 iff using the Active SignConvention
        (b) -1 iff using the Passive SignConvention"""
        return -1 if self == SignConvention.Passive else 1

    @property
    def export_factor(self) -> Literal[-1, 1]:
        """A constant factor which determines the sign of a quantity
        exported under either the Passive or Active SignConvention;
        (a) -1 iff using the Active SignConvention
        (b) 1 iff using the Passive SignConvention"""
        return -1 if self == SignConvention.Active else 1

    def is_export(self, value: float) -> bool:
        """A given value represents some quantity exported iff:
        (a) The SignConvention is Passive and the value is positive, or
        (b) The SignConvention is Active and the value is negative
        """
        is_passive_export = self == SignConvention.Passive and value > 0
        is_active_export = self == SignConvention.Active and value < 0
        return is_passive_export or is_active_export

    def is_import(self, value: float) -> bool:
        """A given value represents some quantity imported iff:
        (a) The SignConvention is Passive and the value is negative, or
        (b) The SignConvention is Active and the value is positive
        """
        is_passive_import = self == SignConvention.Passive and value < 0
        is_active_import = self == SignConvention.Active and value > 0
        return is_passive_import or is_active_import
