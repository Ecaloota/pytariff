from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from pytariff._internal.applied_interval import AppliedInterval
from pytariff.core.day import DayType, DaysApplied

GENERIC_TZ = timezone(offset=timedelta(hours=1))


@pytest.mark.parametrize(
    "start_time, end_time, days_applied",
    [
        (time(12), time(13), DaysApplied(day_types=(DayType.MONDAY,))),
        (time(13), time(12), DaysApplied(day_types=(DayType.MONDAY,))),
        (time(0), time(0), DaysApplied(day_types=(DayType.MONDAY,))),
    ],
)
def test_applied_interval_valid_construction(start_time: time, end_time: time, days_applied: DaysApplied) -> None:
    """"""

    AppliedInterval(start_time=start_time, end_time=end_time, days_applied=days_applied)


@pytest.mark.parametrize(
    "start_time, end_time, days_applied",
    [
        # datetime contains a time, but is not itself a time
        (datetime(2023, 1, 1, 12), time(13), DaysApplied(day_types=(DayType.MONDAY,))),
        (date(2023, 1, 1), time(13), DaysApplied(day_types=(DayType.MONDAY,))),
        (time(12, 1, tzinfo=ZoneInfo("UTC")), time(13), DaysApplied(day_types=(DayType.MONDAY,))),
        (
            time(12, 1, tzinfo=ZoneInfo("UTC")),
            time(13, tzinfo=ZoneInfo("UTC")),
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
        (time(12, 1), time(13, tzinfo=ZoneInfo("UTC")), DaysApplied(day_types=(DayType.MONDAY,))),
    ],
)
def test_applied_interval_invalid_construction(start_time: time, end_time: time, days_applied: DaysApplied) -> None:
    """"""

    with pytest.raises(ValueError):
        AppliedInterval(start_time=start_time, end_time=end_time, days_applied=days_applied)


@pytest.mark.parametrize(
    "candidate_other, is_expected_member, start_time, end_time, days_applied",
    [
        (  # 0. naive candidate time, naive start and end
            time(12, 30),
            True,
            time(12),
            time(13),
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
        (  # 2. aware candidate time, naive start and end
            time(12, 30, tzinfo=GENERIC_TZ),
            False,
            time(12),
            time(13),
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
        (  # 7. AppliedInterval is right-open, so this will fail
            time(13, 0),
            False,
            time(12),
            time(13),
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
        (  # 8. AppliedInterval is right-open, so this will fail
            time(12, 0),
            False,
            time(13),
            time(12),
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
        (  # 9. start == end, we assume interval is 24-hours long (still valid, as interval is right-open)
            # any candidate time is thus in the interval
            time(12, 0),
            True,
            time(12),
            time(12),
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
    ],
)
def test_applied_interval_time_membership(
    candidate_other: time,
    is_expected_member: bool,
    start_time: time,
    end_time: time,
    days_applied: DaysApplied,
) -> None:
    """"""

    ref_intvl = AppliedInterval(start_time=start_time, end_time=end_time, days_applied=days_applied)
    assert (candidate_other in ref_intvl) is is_expected_member


@pytest.mark.parametrize(
    "interval_1, interval_2, expected_intersection",
    [
        (  # identity intersection
            AppliedInterval(
                start_time=time(6),
                end_time=time(7),
                days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
            ),
            AppliedInterval(
                start_time=time(6),
                end_time=time(7),
                days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
            ),
            AppliedInterval(
                start_time=time(6),
                end_time=time(7),
                days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
            ),
        ),
        (  # no intersection in day_type, intersection in time => no intersection
            AppliedInterval(
                start_time=time(6),
                end_time=time(7),
                days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
            ),
            AppliedInterval(
                start_time=time(6),
                end_time=time(7),
                days_applied=DaysApplied(day_types=(DayType.TUESDAY,)),
            ),
            AppliedInterval(
                start_time=None,
                end_time=None,
                days_applied=DaysApplied(day_types=None),
            ),
        ),
        (  # no intersection in day_type, partial intersection in time
            AppliedInterval(
                start_time=time(6),
                end_time=time(7),
                days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
            ),
            AppliedInterval(
                start_time=time(6, 30),
                end_time=time(7),
                days_applied=DaysApplied(day_types=(DayType.TUESDAY,)),
            ),
            AppliedInterval(
                start_time=None,
                end_time=None,
                days_applied=DaysApplied(day_types=None),
            ),
        ),
        (  # intersection in day_type, partial intersection in time
            AppliedInterval(
                start_time=time(6),
                end_time=time(7),
                days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
            ),
            AppliedInterval(
                start_time=time(6, 30),
                end_time=time(7),
                days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
            ),
            AppliedInterval(
                start_time=time(6, 30),
                end_time=time(7),
                days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
            ),
        ),
        (  # no intersection at right-open edges iff no day type intersection
            AppliedInterval(
                start_time=time(6),
                end_time=time(7),
                days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
            ),
            AppliedInterval(
                start_time=time(7),
                end_time=time(8),
                days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
            ),
            AppliedInterval(
                start_time=None,
                end_time=None,
                days_applied=DaysApplied(day_types=None),
            ),
        ),
    ],
)
def test_applied_interval_intersection(interval_1, interval_2, expected_intersection):
    """"""
    assert (interval_1 & interval_2) == expected_intersection
