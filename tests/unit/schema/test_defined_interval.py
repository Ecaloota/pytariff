from datetime import date, datetime, time, timezone
from typing import Any, Optional
from zoneinfo import ZoneInfo

import pytest

from utal.schema.applied_interval import AppliedInterval
from utal.schema.day_type import DayType
from utal.schema.days_applied import DaysApplied
from utal.schema.defined_interval import DefinedInterval


@pytest.mark.parametrize(
    "start, end, tzinfo, tzinfo_start, tzinfo_end",
    [
        # 0. start A, end A
        (
            datetime(2023, 1, 1, tzinfo=ZoneInfo("Australia/Brisbane")),
            datetime(2023, 1, 2, tzinfo=ZoneInfo("Australia/Brisbane")),
            None,
            None,
            None,
        ),
        # 1. start B, end B
        (datetime(2023, 1, 1), datetime(2023, 1, 2), ZoneInfo("Australia/Brisbane"), None, None),
        # 2. start C, end C
        (date(2023, 1, 1), date(2023, 1, 2), ZoneInfo("Australia/Brisbane"), None, None),
        # 3. start A, end B
        (
            datetime(2023, 1, 1, tzinfo=ZoneInfo("Australia/Brisbane")),
            datetime(2023, 1, 2),
            ZoneInfo("Australia/Brisbane"),
            None,
            None,
        ),
        # 4. start A, end C
        (
            datetime(2023, 1, 1, tzinfo=ZoneInfo("Australia/Brisbane")),
            date(2023, 1, 2),
            ZoneInfo("Australia/Brisbane"),
            None,
            None,
        ),
        # 5. start B, end A
        (
            datetime(2023, 1, 1),
            datetime(2023, 1, 2, tzinfo=ZoneInfo("Australia/Brisbane")),
            ZoneInfo("Australia/Brisbane"),
            None,
            None,
        ),
        # 6. start B, end C
        (
            datetime(2023, 1, 1),
            datetime(2023, 1, 2, tzinfo=ZoneInfo("Australia/Brisbane")),
            ZoneInfo("Australia/Brisbane"),
            None,
            None,
        ),
        # 7. start C, end A
        (
            date(2023, 1, 1),
            datetime(2023, 1, 2, tzinfo=ZoneInfo("Australia/Brisbane")),
            ZoneInfo("Australia/Brisbane"),
            None,
            None,
        ),
        # 8. start C, end B
        (date(2023, 1, 1), datetime(2023, 1, 2), ZoneInfo("Australia/Brisbane"), None, None),
        # 9. start A, end A; start == end
        (
            datetime(2023, 1, 1, tzinfo=ZoneInfo("Australia/Brisbane")),
            datetime(2023, 1, 1, tzinfo=ZoneInfo("Australia/Brisbane")),
            None,
            None,
            None,
        ),
        # 10. start B, end B; start == end
        (datetime(2023, 1, 1), datetime(2023, 1, 1), ZoneInfo("Australia/Brisbane"), None, None),
        # 11. start C, end C; start == end
        (date(2023, 1, 1), date(2023, 1, 1), ZoneInfo("Australia/Brisbane"), None, None),
    ],
)
def test_defined_interval_valid_construction(
    start: date | datetime,
    end: date | datetime,
    tzinfo: Optional[timezone],
    tzinfo_start: Optional[timezone],
    tzinfo_end: Optional[timezone],
):
    """
    Type A: Timezone-aware datetime
    Type B: Naive datetime, tzinfo provided extra. Optionally, B's timezone need not match
            provided tzinfo
    Type C: Date, tzinfo provided extra.

    In all cases, start <= end.
    The timezones of the start and end values do not need to match
    """

    # we assume by construction that the start/end is a naive datetime only (not date) in this case
    if tzinfo_start is not None:
        start = start.combine(start.date(), start.time(), tzinfo=tzinfo_start)
    if tzinfo_end is not None:
        end = end.combine(end.date(), end.time(), tzinfo=tzinfo_end)

    assert DefinedInterval(start=start, end=end, tzinfo=tzinfo)


@pytest.mark.parametrize(
    "start, end, tzinfo, tzinfo_start, tzinfo_end",
    [
        (  # 0. start is not a datetime or a date
            int(99),
            datetime(2023, 1, 2, tzinfo=ZoneInfo("Australia/Brisbane")),
            None,
            None,
            None,
        ),
        (  # 1. end is not a datetime or a date
            datetime(2023, 1, 1, tzinfo=ZoneInfo("Australia/Brisbane")),
            int(99),
            None,
            None,
            None,
        ),
        (  # 2. start is a date, but no tzinfo provided
            date(2023, 1, 1),
            datetime(2023, 1, 2, tzinfo=ZoneInfo("Australia/Brisbane")),
            None,
            None,
            None,
        ),
        (  # 3. end is a date, but no tzinfo provided
            datetime(2023, 1, 1, tzinfo=ZoneInfo("Australia/Brisbane")),
            date(2023, 1, 2),
            None,
            None,
            None,
        ),
        (  # 4. start is a naive datetime, but no tzinfo provided
            datetime(2023, 1, 1, tzinfo=None),
            datetime(2023, 1, 2, tzinfo=ZoneInfo("Australia/Brisbane")),
            None,
            None,
            None,
        ),
        (  # 5. end is a naive datetime, but no tzinfo provided
            datetime(2023, 1, 1, tzinfo=ZoneInfo("Australia/Brisbane")),
            datetime(2023, 1, 2, tzinfo=None),
            None,
            None,
            None,
        ),
        (  # 6. end < start
            datetime(2023, 1, 2, tzinfo=ZoneInfo("Australia/Brisbane")),
            datetime(2023, 1, 1, tzinfo=ZoneInfo("Australia/Brisbane")),
            None,
            None,
            None,
        ),
        (  # 7. start B, end B; tzinfo of start does not match provided
            datetime(2023, 1, 1),
            datetime(2023, 1, 2),
            ZoneInfo("Australia/Brisbane"),
            ZoneInfo("UTC"),
            None,
        ),
        (  # 8. start B, end B; tzinfo of end does not match provided
            datetime(2023, 1, 1),
            datetime(2023, 1, 2),
            ZoneInfo("Australia/Brisbane"),
            None,
            ZoneInfo("UTC"),
        ),
        (  # 9. start B, end C; tzinfo of start does not match provided
            datetime(2023, 1, 1),
            date(2023, 1, 2),
            ZoneInfo("Australia/Brisbane"),
            ZoneInfo("UTC"),
            None,
        ),
        (  # 10. start C, end B; tzinfo of end does not match provided
            date(2023, 1, 1),
            datetime(2023, 1, 2),
            ZoneInfo("Australia/Brisbane"),
            None,
            ZoneInfo("UTC"),
        ),
    ],
)
def test_defined_interval_invalid_construction_raises_value_error(
    start: Any, end: Any, tzinfo: Any, tzinfo_start: Any, tzinfo_end: Any
) -> None:
    """"""

    # we assume by construction that the start/end is a naive datetime only (not date) in this case
    if tzinfo_start is not None:
        start = start.combine(start.date(), start.time(), tzinfo=tzinfo_start)
    if tzinfo_end is not None:
        end = end.combine(end.date(), end.time(), tzinfo=tzinfo_end)

    with pytest.raises(ValueError):
        DefinedInterval(start=start, end=end, tzinfo=tzinfo)


@pytest.mark.parametrize(
    "child_intervals",
    [
        (  # days_applied intersection but no time intersection
            (
                AppliedInterval(
                    start_time=time(6),
                    end_time=time(7),
                    days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
                    tzinfo=ZoneInfo("Australia/Brisbane"),
                ),
                AppliedInterval(
                    start_time=time(8),
                    end_time=time(9),
                    days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
                    tzinfo=ZoneInfo("Australia/Brisbane"),
                ),
            )
        ),
        (  # days_applied intersection but no time intersection
            (
                AppliedInterval(
                    start_time=time(6),
                    end_time=time(7),
                    days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
                    tzinfo=ZoneInfo("Australia/Brisbane"),
                ),
                AppliedInterval(
                    start_time=time(7),
                    end_time=time(8),
                    days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
                    tzinfo=ZoneInfo("Australia/Brisbane"),
                ),
            )
        ),
        (  # time intersection but no days_applied intersection
            (
                AppliedInterval(
                    start_time=time(6),
                    end_time=time(7),
                    days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
                    tzinfo=ZoneInfo("Australia/Brisbane"),
                ),
                AppliedInterval(
                    start_time=time(6),
                    end_time=time(7),
                    days_applied=DaysApplied(day_types=(DayType.TUESDAY,)),
                    tzinfo=ZoneInfo("Australia/Brisbane"),
                ),
            )
        ),
        (  # no days_applied intersection and no time intersection
            (
                AppliedInterval(
                    start_time=time(6),
                    end_time=time(7),
                    days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
                    tzinfo=ZoneInfo("Australia/Brisbane"),
                ),
                AppliedInterval(
                    start_time=time(7),
                    end_time=time(8),
                    days_applied=DaysApplied(day_types=(DayType.TUESDAY,)),
                    tzinfo=ZoneInfo("Australia/Brisbane"),
                ),
            )
        ),
    ],
)
def test_defined_interval_allows_non_overlapping_children(child_intervals: tuple[AppliedInterval, ...]):
    """TODO"""
    DefinedInterval(
        start=datetime(2023, 1, 1),
        end=datetime(2023, 12, 31),
        tzinfo=ZoneInfo("Australia/Brisbane"),
        children=child_intervals,
    )


@pytest.mark.parametrize(
    "child_intervals",
    [
        (  # overlap due to identity
            (
                AppliedInterval(
                    start_time=time(6),
                    end_time=time(7),
                    days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
                    tzinfo=ZoneInfo("Australia/Brisbane"),
                ),
                AppliedInterval(
                    start_time=time(6),
                    end_time=time(7),
                    days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
                    tzinfo=ZoneInfo("Australia/Brisbane"),
                ),
            )
        ),
        (  # overlap due to partial overlap in both times and day_types
            (
                AppliedInterval(
                    start_time=time(6),
                    end_time=time(7),
                    days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
                    tzinfo=ZoneInfo("Australia/Brisbane"),
                ),
                AppliedInterval(
                    start_time=time(6, 30),
                    end_time=time(7, 30),
                    days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
                    tzinfo=ZoneInfo("Australia/Brisbane"),
                ),
            )
        ),
    ],
)
def test_defined_interval_children_cannot_overlap(child_intervals: tuple[AppliedInterval, ...]):
    """TODO"""

    with pytest.raises(ValueError):
        DefinedInterval(
            start=datetime(2023, 1, 1),
            end=datetime(2023, 12, 31),
            tzinfo=ZoneInfo("Australia/Brisbane"),
            children=child_intervals,
        )


@pytest.mark.parametrize(
    "child_intervals",
    [
        (  # not sharing the same timezone
            (
                AppliedInterval(
                    start_time=time(6),
                    end_time=time(7),
                    days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
                    tzinfo=ZoneInfo("Australia/Canberra"),
                ),
                AppliedInterval(
                    start_time=time(8),
                    end_time=time(9),
                    days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
                    tzinfo=ZoneInfo("Australia/Brisbane"),
                ),
            )
        ),
    ],
)
def test_defined_interval_children_must_share_timezones(child_intervals: tuple[AppliedInterval, ...]):
    """TODO"""

    with pytest.raises(ValueError):
        DefinedInterval(
            start=datetime(2023, 1, 1),
            end=datetime(2023, 12, 31),
            tzinfo=ZoneInfo("Australia/Brisbane"),
            children=child_intervals,
        )
