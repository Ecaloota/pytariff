from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Generator

from whenever import ZonedDateTime

from pytariff.transformers import (
    CumSumTransformer,
    IdentityTransformer,
    MaxTransformer,
    MeanTransformer,
    RollingMaxTransformer,
    _InfiniteTransformer,
)


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

    _MINUTELY = {"minutes": 1}  # not intended for public use

    @classmethod
    def _missing_(cls, value: object) -> Any:
        if not isinstance(value, str):
            return None

        try:
            return cls.__members__[value.upper()]
        except KeyError:
            pass
        return None


# TODO is this a ChargeMethod? Or a TransformMethod?
# Seems more generic than working out how to charge a profile
class ChargeMethod(Enum):
    Identity = IdentityTransformer
    Mean = MeanTransformer
    Max = MaxTransformer
    RollingMax = RollingMaxTransformer
    CumSum = CumSumTransformer

    _Infinity = _InfiniteTransformer  # not intended for public use

    def __call__(
        cls,
        profile: dict[ZonedDateTime, float],
        transform_start: ZonedDateTime,
        transform_end: ZonedDateTime,
        transformer_kwargs: dict[str, Any] = {},
    ) -> dict[ZonedDateTime, float]:
        """TODO"""

        y_pred = cls.value(**transformer_kwargs).transform(
            profile, transform_start, transform_end
        )

        return y_pred


# TODO is this a ResetPeriod? Maybe a ResetDefinition?
@dataclass
class ResetPeriod:
    anchor: ZonedDateTime
    frequency: ResetFrequency
    charge_method: ChargeMethod = ChargeMethod.Identity

    def next_reset(self) -> Generator[ZonedDateTime, None, None]:
        """Obtain the next change-over time point relative to self.anchor
        with frequency self.frequency

        For example:
        >>> reset_period = ResetPeriod(
                anchor=ZonedDateTime(2024, 1, 1, tz="UTC"),
                frequency=ResetFrequency.DAILY,
            )
        >>> next(reset_period.next_reset())
        >>> ZonedDateTime(2024, 1, 2, tz="UTC")
        """
        current = self.anchor
        current = current.add(**self.frequency.value, disambiguate="compatible")
        yield current

    # TODO we need to be careful how we handle edge effects here
    # TODO lots of testing required
    def get_transformed_profile(
        self,
        profile: dict[ZonedDateTime, float],
        until: ZonedDateTime | None = None,
        transformer_kwargs: dict[str, Any] = {},
    ) -> dict[ZonedDateTime, float]:
        """TODO"""

        # if until is not provided, we transform the entire profile
        until = until or max(profile.keys())

        # initialise the profile up to the first anchor (exclusive; nothing to do)
        # and until the end of the `until` period (exclusive; nothing to do)
        transformed: dict[ZonedDateTime, float] = {
            k: profile[k] for k in profile if k < self.anchor
        } | {k: profile[k] for k in profile if k > until}

        while self.anchor <= until:
            for reset_time in self.next_reset():
                transformed.update(
                    self.charge_method(
                        profile, self.anchor, reset_time, transformer_kwargs
                    )
                )
                self.anchor = reset_time

        return transformed
