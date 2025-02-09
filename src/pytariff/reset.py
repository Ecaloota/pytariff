from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Generator

from whenever import ZonedDateTime


class ResetFrequency(Enum):
    """The ResetFrequency of some TariffInterval is defined to be the *calendar*
    frequency at which the TariffInterval ChargeMethod is re-calculated.

    Date and time arithmetic can be challenging due to DST and other timezone changes.
    There are three mains cases to consider, which are taken directly from the
    whenever[https://whenever.readthedocs.io/en/latest/overview.html] docs:

    1. Adding years and months may result in date trunctation
        >>> d = whenever.LocalDateTime(2023, 8, 31, hour=12)
        >>> d.add(months=1)
        whenever.LocalDateTime(2023-09-30 12:00:00)

    In (rare) cases where the resulting date occurs in the middle of a DST transition,
    we opt to take the earlier time for backward transitions and the later time for
    forward transitions, compatible with RFC 5545 (using the "compatible" argument
    provided by whenever).

    2. Adding days only affects the calendar date (not the local time of day), which
    is the intuitive behaviour except during DST transitions. For this reason, adding
    24 hours is not equivalent to adding 1 day. As with point 1, this is both RFC 5545
    compliant, and the behaviour provided by whenever.

    3. Adding precise time units (hours, mins, secs) is always correct.
    """

    DAILY = {"days": 1}
    WEEKLY = {"weeks": 1}
    MONTHLY = {"months": 1}
    QUARTERLY = {"months": 3}

    @classmethod
    def _missing_(cls, value: object) -> Any:
        if not isinstance(value, str):
            return None

        try:
            return cls.__members__[value]
        except KeyError:
            pass
        return None


# TODO as yet unclear what this should do (other than current function of simply
# providing allowed mapping values). Should it define the lambda which it names?
# In that case, we would provide a ZonedDateTime interval (from start of ResetPeriod
# to end), then provide a callable via this Enum which, when applied to a profile over
# that range, would determine the value at which that period would be levied.
# For example, ChargeMethod.Mean would take some interval [a, b), and determine the
# average [Metric] (Consumption / Demand), X_bar over [a, b) and return X_bar.
# (For this to work, we would need to provide a method to get the value of the Metric
# over that interval and pass it to the Enum?..)
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
    # charge_method: ChargeMethod # TODO does this belong here?

    # TODO we may need a method here to determine change-over time points
    # for example, given an anchor of 2021-01-01T00:00:00Z and frequency DAILY,
    # the next change point is 2021-01-02T00:00:00Z. We could construct this as
    # a generator and retrieve from it as required when performing a simulation.

    def next_reset(self) -> Generator[ZonedDateTime, None, None]:
        current = self.anchor
        while True:
            current = current.add(**self.frequency.value)
            yield current
