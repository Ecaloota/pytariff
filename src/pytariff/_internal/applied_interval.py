from datetime import time
from typing import Optional
from uuid import uuid4

from pydantic import UUID4, BaseModel, ConfigDict, PrivateAttr, field_validator, model_validator

from pytariff._internal import helper
from pytariff.core.day import DaysApplied  # _internal shouldn't import from core...


class AppliedInterval(BaseModel):
    """An AppliedInterval is a right-open datetime.time interval over ``[start_time, end_time)``, (or over
    ``[end_time, start_time)`` if ``end_time`` < ``start_time``) that is defined as active in the period specified
    in the provided ``DaysApplied``.

    If ``start_time`` == ``end_time``, the ``AppliedInterval`` is considered active at all times in the
    provided ``DaysApplied``.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    start_time: Optional[time]
    """The beginning of the ``AppliedInterval``. Must be naive."""

    end_time: Optional[time]
    """The end of the ``AppliedInterval``. Must be naive."""

    days_applied: DaysApplied
    """See :class:`.DaysApplied`"""

    _uuid: UUID4 = PrivateAttr(default_factory=uuid4)

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_times_naive(cls, v: time | None) -> time | None:
        """If ``v`` is present, validate that it is naive, else return it.

        Raises:
            ValueError: If ``start_time`` is timezone-aware.

        Returns:
            datetime.time | None
        """
        if v is None:
            return v

        if helper.is_aware(v):
            raise ValueError

        return v

    @model_validator(mode="after")
    def validate_time_relationship(self) -> "AppliedInterval":
        """If ``start_time`` is equal to ``end_time``, we set the instance ``start_time`` and ``end_time`` to
        ``datetime.time.min`` and ``datetime.time.max``, respectively.

        Returns:
            ``AppliedInterval``
        """

        # We assume that if below condition, the user is trying to specify that the
        # AppliedInterval is to be applied at all possible times. This is the closest we
        # can do with datetime.time, noting that it is unlikely to cause significant error

        if self.start_time == self.end_time:
            self.start_time = time.min
            self.end_time = time.max
        return self

    def __contains__(self, other: time) -> bool:
        """
        An ``AppliedInterval`` contains a candidate ``datetime.time`` if and only if that time is within the range
        ``[start_time, end_time)`` and the candidate time is naive.

        Args:
            other: The candidate value
        """

        if self.start_time is None or self.end_time is None:
            return False

        if not isinstance(other, time) or helper.is_aware(other):
            return False

        if self.start_time <= self.end_time:
            if self.start_time == self.end_time:
                return True
            return self.start_time <= other < self.end_time
        return self.start_time <= other or other < self.end_time

    def __and__(self, other: "AppliedInterval") -> Optional["AppliedInterval"]:
        """The intersection between a pair of right-open intervals [a, b) and [c,d) is the span of
        all values belonging to both, being ``[max(a, c), min(b, d))``, and the intersection between a
        pair of DaysApplied is the result of their intersection operation.

        Then, the intersection between a pair of ``AppliedInterval`` is the ``AppliedInterval`` with
        ``start_time = max(a, c)``, ``end_time = min(b, d)``, and ``days_applied =
        self.days_applied & other.days_applied``
        """

        if not isinstance(other, AppliedInterval):
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
            )

        return AppliedInterval(
            start_time=start_intersection,
            end_time=end_intersection,
            days_applied=day_intersection,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AppliedInterval):
            return False

        return (
            self.start_time == other.start_time
            and self.end_time == other.end_time
            and self.days_applied == other.days_applied
        )

    def __hash__(self) -> int:
        return hash(self.start_time) ^ hash(self.end_time) ^ hash(self.days_applied)

    def _is_empty(self) -> bool:
        """An AppliedInterval is empty if the following are all True:
        (a) self.start_time is None
        (b) self.end_time is None
        (c) tzinfo is None
        (d) self.days_applied.day_types is None (the non-/existence of holidays is irrelevant)
        """

        return self.start_time is None and self.end_time is None and self.days_applied.day_types is None

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
