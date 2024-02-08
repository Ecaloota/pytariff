from datetime import date, datetime, time
from typing import Optional
from uuid import uuid4
from zoneinfo import ZoneInfo
import pandas as pd

from pydantic import UUID4, BaseModel, ConfigDict, PrivateAttr, ValidationInfo, field_validator, model_validator

from pytariff._internal import helper
from pytariff._internal.applied_interval import AppliedInterval


class DefinedInterval(BaseModel):
    """A ``DefinedInterval`` is a closed datetime.datetime interval over ``[start, end]``
    that must always be timezone-aware, and contains ``children`` :ref:`applied_interval`.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    tzinfo: Optional[ZoneInfo] = None
    """Timezone information associated with the current interval. Does not need to be provided unless one or both of
    ``start`` and ``end`` are naive. Default None."""

    start: datetime
    """The beginning of the ``DefinedInterval``. If ``start`` is naive, ``tzinfo`` must be provided. If ``start``
    is timezone-aware, its timezone information must match the timezone information provided in ``end``, if present,
    or the timezone information in ``tzinfo``, if present."""

    end: datetime
    """The end of the ``DefinedInterval``. If ``end`` is naive, ``tzinfo`` must be provided. If ``end`` is
    timezone-aware, its timezone information must match the timezone information provided in ``start``, if present, or
    the timezone information in ``tzinfo``, if present."""

    children: Optional[tuple[AppliedInterval, ...]] = None
    """Defines when a tariff may be applied within the definition interval. Multiple ``children`` cannot overlap. See
    :ref:`applied_interval`."""

    _uuid: UUID4 = PrivateAttr(default_factory=uuid4)

    @field_validator("start", "end")
    @classmethod
    def validate_datetime_is_aware(cls, v: datetime, info: ValidationInfo) -> datetime:
        """Validate that ``v`` is timezone-aware, or if it is naive, that the instance has valid ``tzinfo``.
        Returns the datetime.datetime instance with timezone information.

        Raises:
            ValueError: If ``v`` is naive and the instance does not contain ``tzinfo``.

        Returns:
            datetime.datetime
        """

        if helper.is_naive(v) and info.data.get("tzinfo", None) is None:
            raise ValueError
        elif helper.is_naive(v):
            v = helper.convert_to_aware_datetime(obj=v, tzinfo=info.data.get("tzinfo"))
        return v

    @model_validator(mode="after")
    def validate_timezones_match(self) -> "DefinedInterval":
        """Validate that the timezone of the instance ``self.start`` and ``self.end`` has exactly matching timezone
        information.

        Raises:
            ValueError: If ``self.start.tzinfo != self.end.tzinfo``.

        Returns:
            ``DefinedInterval``
        """
        if not self.start.tzinfo == self.end.tzinfo:
            raise ValueError
        return self

    @model_validator(mode="after")
    def validate_start_le_end(self) -> "DefinedInterval":
        """Validate that the instance ``self.start`` is less than or equal to ``self.end``

        Raises:
            ValueError: If ``self.end < self.start``.

        Returns:
            ``DefinedInterval``
        """
        if self.end < self.start:
            raise ValueError
        return self

    @model_validator(mode="after")
    def validate_children_cannot_overlap(self) -> "DefinedInterval":
        """Validate that no pair of ``AppliedInterval`` children overlaps in the instance ``children`` tuple.
        For the definition of the overlap between two ``AppliedInterval``, see :ref:`applied_interval`

        Raises:
            ValueError: If any pair of unique ``AppliedInterval`` overlaps.

        Returns:
            ``DefinedInterval``
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

    def __contains__(self, other: datetime | date | pd.Timestamp, tzinfo: Optional[ZoneInfo] = None) -> bool:
        """
        * A ``DefinedInterval`` contains a ``datetime.datetime`` ``other`` if and only if the ``datetime.datetime`` is
          within the range ``self.start <= other <= self.end``.
        * A ``DefinedInterval`` contains a ``datetime.date`` ``other`` if and only if the ``datetime.date`` is
          timezone-aware and the derived datetime (created via ``datetime.combine`` with the instance ``tzinfo``)
          at midnight is within ``self.start <= other <= self.end``
        * A ``DefinedInterval`` contains a ``pandas.Timestamp`` ``other`` if and only if the ``pandas.Timestamp`` is
          ``to_pydatetime()``-coercible to a ``datetime.date``, and passes the requirements of a ``datetime.date``
          above.

        Raises:
            ValueError: If any of the above conditions fail
        """

        if not (helper.is_datetime_type(other) or helper.is_date_type(other)):
            raise ValueError

        if helper.is_date_type(other) and tzinfo is None:
            raise ValueError

        elif isinstance(other, date) and isinstance(other, pd.Timestamp):
            other: pd.Timestamp = other.to_pydatetime()  # type: ignore

        elif isinstance(other, date):
            other = datetime.combine(date=other, time=time(0, 0, 0), tzinfo=tzinfo)

        return self.start <= other <= self.end
