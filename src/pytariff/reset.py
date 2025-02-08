from dataclasses import dataclass
from enum import Enum

from whenever import ZonedDateTime


class ResetFrequency(Enum):
    DAILY = "1D"
    WEEKLY = "7D"
    MONTHLY = "1M"
    QUARTERLY = "3M"


class ChargeMethod(str, Enum):
    Identity = "Identity"
    Mean = "Mean"
    Max = "Max"
    RollingMax = "RollingMax"
    CumSum = "CumSum"


@dataclass
class ResetPeriod:
    anchor: ZonedDateTime
    frequency: ResetFrequency
    charge_method: ChargeMethod

    # TODO we may need a method here to determine change-over time points
    # for example, given an anchor of 2021-01-01T00:00:00Z and frequency DAILY,
    # the next change point is 2021-01-02T00:00:00Z. We could construct this as
    # a generator and retrieve from it as required when performing a simulation.
