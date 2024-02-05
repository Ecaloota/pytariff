from datetime import date, datetime, time, timezone
from typing import Optional
from uuid import uuid4
from zoneinfo import ZoneInfo

from pydantic import UUID4, BaseModel, ConfigDict, Field, model_validator

from pytariff._internal import helper
from pytariff.core.day import DaysApplied  # _internal shouldn't import from core...


class AppliedInterval(BaseModel):
    """An AppliedInterval is a right-open time interval over [start_time, end_time) where
    start_time <= end_time, or over (end_time, start_time] where end_time < start_time.
    An AppliedInterval must always be timezone aware.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    start_time: Optional[time]
    end_time: Optional[time]
    days_applied: DaysApplied
    tzinfo: Optional[timezone | ZoneInfo] = None

    uuid: UUID4 = Field(default_factory=uuid4)

    @model_validator(mode="after")
    def validate_start_time_aware(self) -> "AppliedInterval":
        if self.start_time is None:
            return self

        if helper.is_naive(self.start_time) and self.tzinfo is None:
            raise ValueError
        elif helper.is_naive(self.start_time):
            self.start_time = self.start_time.replace(tzinfo=self.tzinfo)

        return self

    @model_validator(mode="after")
    def validate_end_time_aware(self) -> "AppliedInterval":
        if self.end_time is None:
            return self

        if helper.is_naive(self.end_time) and self.tzinfo is None:
            raise ValueError
        elif helper.is_naive(self.end_time):
            self.end_time = self.end_time.replace(tzinfo=self.tzinfo)

        return self

    @model_validator(mode="after")
    def validate_time_relationship(self) -> "AppliedInterval":
        """We assume that if below condition, the user is trying to specify that the
        AppliedInterval is to be applied at all possible times. This is the closest we
        can do with datetime.time, noting that it is unlikely to cause significant error"""

        tz_attrs = [
            getattr(self.start_time, "tzinfo", None),
            getattr(self.end_time, "tzinfo", None),
            getattr(self, "tzinfo", None),
        ]
        tz_list = [x for x in tz_attrs if x is not None]

        if len(tz_list) == 0:
            raise ValueError
        else:
            tz = tz_list.pop()

        if self.start_time == self.end_time:
            self.start_time = time.min.replace(tzinfo=tz)
            self.end_time = time.max.replace(tzinfo=tz)
        return self

    def __contains__(self, other: time | date | datetime) -> bool:
        """
        An AppliedInterval contains a time iff that time is within the range [start_time, end_time).
        An AppliedInterval contains a date iff the date's day appears in the days_applied.
        An AppliedInterval contains a datetime iff both of the above are true for the time of the
            datetime and the date of the datetime, respectively.

        An other which is not a time, date, or datetime is not contained within an AppliedInterval.
        An other which is a naive time or naive datetime is not contained within an AppliedInterval.
        """

        if self.start_time is None or self.end_time is None:
            return False

        if not (helper.is_datetime_type(other) or helper.is_date_type(other) or isinstance(other, time)):
            return False

        if helper.is_naive(other) and not helper.is_date_type(other):  # type: ignore # TODO this is likely valid
            return False

        if isinstance(other, time):
            if self.start_time <= self.end_time:
                if self.start_time == self.end_time:
                    return True
                return self.start_time <= other < self.end_time
            return self.start_time <= other or other < self.end_time

        elif helper.is_date_type(other):
            return other in self.days_applied

        elif helper.is_datetime_type(other):
            if self.start_time <= self.end_time:
                return self.start_time <= other.timetz() < self.end_time and other in self.days_applied
            return (self.start_time <= other.timetz() or other.timetz() < self.end_time) and other in self.days_applied

        return False

    def __and__(self, other: "AppliedInterval") -> Optional["AppliedInterval"]:
        """The intersection between two right-open intervals [a, b) and [c, d) is the set of all values that belong
        to both, being:
            [max(a, c), min(b, d))

        And the intersection between two DaysApplied is the result of their intersection operation.

        Then, the intersection between two AppliedIntervals is the AppliedInterval with start_time = max(a, c),
        end_time = min(b, d), and days_applied = self.days_applied & other.days_applied.

        Two AppliedIntervals must share a timezone, (for my convenience, mostly)
        """

        if not isinstance(other, AppliedInterval):
            raise ValueError

        # The intersection between two applied intervals defined in different tzinfo is empty
        # TODO we can generalise this to be correct, with effort
        if self.tzinfo != other.tzinfo:
            raise ValueError

        if any([x is None for x in [self.start_time, self.end_time, other.start_time, other.end_time]]):
            raise ValueError

        start_intersection = max(self.start_time, other.start_time)  # type: ignore
        end_intersection = min(self.end_time, other.end_time)  # type: ignore
        day_intersection = self.days_applied & other.days_applied

        def _is_day_intersection() -> bool:
            return day_intersection.day_types is not None or day_intersection.holidays is not None

        def _is_time_intersection() -> bool:
            return start_intersection <= end_intersection  # type: ignore

        # We need to check for time intersections AND day intersections
        # There is no intersection if there is no day intersection
        if (
            not _is_day_intersection()
            or (_is_day_intersection() and start_intersection == end_intersection)
            or not _is_time_intersection()
        ):
            return AppliedInterval(
                start_time=None,
                end_time=None,
                days_applied=DaysApplied(day_types=None, holidays=None),
                tzinfo=self.tzinfo,
            )

        return AppliedInterval(
            start_time=start_intersection,
            end_time=end_intersection,
            days_applied=day_intersection,
            tzinfo=self.tzinfo,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AppliedInterval):
            return False

        return (
            self.start_time == other.start_time
            and self.end_time == other.end_time
            and self.days_applied == other.days_applied
            and self.tzinfo == other.tzinfo
        )

    def __hash__(self) -> int:
        return hash(self.start_time) ^ hash(self.end_time) ^ hash(self.days_applied) ^ hash(self.tzinfo)

    def _is_empty(self) -> bool:
        """An AppliedInterval is empty if the following are all True:
        (a) self.start_time is None
        (b) self.end_time is None
        (c) tzinfo is None
        (d) self.days_applied.day_types is None (the non-/existence of holidays is irrelevant)
        """

        return (
            self.start_time is None
            and self.end_time is None
            and self.tzinfo is None
            and self.days_applied.day_types is None
        )

    def _contains_day_type_only(self) -> bool:
        """For the purposes of testing for overlap between AppliedIntervals, an overlap is
        defined as when:
            1. max(self.start_time, other.start_time) <= min(self.end_time, other.end_time), AND
            2. (self.day_types & other.day_types) is not None
            3. (self.day_types & other.day_types).day_types is not None
        """

        return self.days_applied is not None and self.start_time is None and self.end_time is None

    def _contains_time_only(self) -> bool:
        """"""
        return (
            self.start_time is not None
            and self.end_time is not None
            and (self.days_applied is None or self.days_applied.day_types is None)
        )
