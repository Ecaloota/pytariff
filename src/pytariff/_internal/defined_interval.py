from datetime import date, datetime, time, timezone
from typing import Optional
from uuid import uuid4
from zoneinfo import ZoneInfo
import pandas as pd

from pydantic import UUID4, BaseModel, ConfigDict, PrivateAttr, model_validator

from pytariff._internal import helper
from pytariff._internal.applied_interval import AppliedInterval


class DefinedInterval(BaseModel):
    """A ``DefinedInterval`` is a closed datetime.datetime interval over ``[start, end]``
    that must always be timezone-aware, and contains ``children`` :ref:`applied_interval`.

    Args:
        start: The beginning of the ``DefinedInterval``. If ``start`` is naive,
            ``tzinfo`` must be provided. If ``start`` is timezone-aware, it's timezone information must match
            the timezone information provided in ``end``, if present, or the timezone information in ``tzinfo``,
            if present.
        end: The end of the ``DefinedInterval``. If ``end`` is naive,
            ``tzinfo`` must be provided. If ``end`` is timezone-aware, it's timezone information must match
            the timezone information provided in ``start``, if present, or the timezone information in ``tzinfo``,
            if present.
        tzinfo: Timezone information associated with the current interval.
            Does not need to be provided unless one or both of ``start`` and ``end`` are timezone-aware.
            Default None.
        children: Defines when a tariff may be applied within the definition
            interval. Multiple ``children`` cannot overlap. See :ref:`applied_interval`.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    start: datetime
    end: datetime
    tzinfo: Optional[timezone | ZoneInfo] = None
    children: Optional[tuple[AppliedInterval, ...]] = None

    _uuid: UUID4 = PrivateAttr(default_factory=uuid4)

    @model_validator(mode="after")
    def validate_model_is_aware(self) -> "DefinedInterval":
        if (helper.is_naive(self.start) or helper.is_naive(self.end)) and self.tzinfo is None:
            raise ValueError
        return self

    @model_validator(mode="after")
    def validate_start_aware(self) -> "DefinedInterval":
        self.start = helper.convert_to_aware_datetime(obj=self.start, tzinfo=self.tzinfo)
        return self

    @model_validator(mode="after")
    def validate_end_aware(self) -> "DefinedInterval":
        self.end = helper.convert_to_aware_datetime(obj=self.end, tzinfo=self.tzinfo)
        return self

    @model_validator(mode="after")
    def validate_timezones_match(self) -> "DefinedInterval":
        if not self.start.tzinfo == self.end.tzinfo:
            raise ValueError
        return self

    @model_validator(mode="after")
    def validate_start_le_end(self) -> "DefinedInterval":
        if self.end < self.start:
            raise ValueError
        return self

    @model_validator(mode="after")
    def validate_children_cannot_overlap(self) -> "DefinedInterval":
        """An overlap between AppliedIntervals is defined as when:
        TODO
        """
        if self.children is None:
            return self

        for i, x in enumerate(self.children):
            for j, y in enumerate(self.children):
                if i != j:
                    intersection = x & y
                    if (
                        intersection is None
                        or intersection._is_empty()
                        or intersection._contains_day_type_only()
                        or intersection._contains_time_only()
                    ):
                        continue
                    else:
                        raise ValueError

        return self

    @model_validator(mode="after")
    def validate_children_share_tzinfo(self) -> "DefinedInterval":
        if self.children is None:
            return self

        for i, x in enumerate(self.children):
            for j, y in enumerate(self.children):
                if i != j:
                    if x.tzinfo != y.tzinfo:
                        raise ValueError
        return self

    def __contains__(self, other: datetime | date | pd.Timestamp, tzinfo: Optional[timezone | ZoneInfo] = None) -> bool:
        """foo"""
        # """
        # A DefinedInterval contains a datetime iff the datetime is within
        #     self.start <= other <= self.end.
        # A DefinedInterval contains a date iff the date is provided with an associated timezone,
        #     and the derived datetime at midnight in that timezone is within
        #     self.start <= other <= self.end.
        # """

        if not (helper.is_datetime_type(other) or helper.is_date_type(other)):
            raise ValueError

        if helper.is_date_type(other) and tzinfo is None:
            raise ValueError

        elif isinstance(other, date) and isinstance(other, pd.Timestamp):
            other: pd.Timestamp = other.to_pydatetime()  # type: ignore

        elif isinstance(other, date):
            other = datetime.combine(date=other, time=time(0, 0, 0), tzinfo=tzinfo)

        return self.start <= other <= self.end
