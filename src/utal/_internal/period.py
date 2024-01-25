from enum import Enum

from pydantic.dataclasses import dataclass


class ResetPeriod(Enum):
    ...


class ConsumptionResetPeriod(ResetPeriod):
    """Allows us to define tariffs of the sort
    $X/kWh for the [N, M] kWh per ConsumptionResetPeriod"""

    DAILY = "1D"
    MONTHLY = "MS"
    QUARTERLY = "QS"
    ANNUALLY = "YS"


@dataclass
class DemandResetPeriod(ResetPeriod):
    """Allows us to define tariffs of the sort
    $X/kWh if kW peak in some range, reset after DemandResetPeriod"""

    QUARTER_HOURLY = "15min"
    HALF_HOURLY = "30min"
    HOURLY = "1h"
    DAILY = "1D"
