from datetime import timedelta
from enum import Enum


class ConsumptionResetPeriod(Enum):
    """Allows us to define tariffs of the sort
    $X/kWh for the [N, M] kWh per ConsumptionResetPeriod"""

    DAILY = "DAILY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUALLY = "ANNUALLY"


class DemandResetPeriod(Enum):
    """Allows us to define tariffs of the sort
    $X/kWh if kW peak in some range, reset after DemandResetPeriod"""

    QUARTER_HOURLY = timedelta(minutes=15)
    HALF_HOURLY = timedelta(minutes=30)
    HOURLY = timedelta(minutes=60)
    DAILY = timedelta(days=1)
