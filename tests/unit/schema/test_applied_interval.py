from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest
from holidays import country_holidays

from utal.schema.applied_interval import AppliedInterval
from utal.schema.day_type import DayType
from utal.schema.days_applied import DaysApplied

GENERIC_TZ = timezone(offset=timedelta(hours=1))


@pytest.mark.parametrize(
    "start_time, end_time, tzinfo, days_applied",
    [
        (time(12), time(13), GENERIC_TZ, DaysApplied(day_types=(DayType.MONDAY,))),
        (time(13), time(12), GENERIC_TZ, DaysApplied(day_types=(DayType.MONDAY,))),
        (
            time(12, tzinfo=GENERIC_TZ),
            time(13, tzinfo=GENERIC_TZ),
            None,
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
        (
            time(12, tzinfo=GENERIC_TZ),
            time(13, tzinfo=GENERIC_TZ),
            None,
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
        (
            time(0, tzinfo=GENERIC_TZ),
            time(0, tzinfo=GENERIC_TZ),
            None,
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
    ],
)
def test_applied_interval_valid_construction(
    start_time: time, end_time: time, tzinfo: timezone, days_applied: DaysApplied
) -> None:
    """"""

    AppliedInterval(start_time=start_time, end_time=end_time, days_applied=days_applied, tzinfo=tzinfo)


@pytest.mark.parametrize(
    "start_time, end_time, tzinfo, days_applied",
    [
        # datetime contains a time, but is not itself a time
        (datetime(2023, 1, 1, 12), time(13), GENERIC_TZ, DaysApplied(day_types=(DayType.MONDAY,))),
        (date(2023, 1, 1), time(13), GENERIC_TZ, DaysApplied(day_types=(DayType.MONDAY,))),
    ],
)
def test_applied_interval_invalid_construction(
    start_time: time, end_time: time, tzinfo: timezone, days_applied: DaysApplied
) -> None:
    """"""

    with pytest.raises(ValueError):
        AppliedInterval(start_time=start_time, end_time=end_time, days_applied=days_applied, tzinfo=tzinfo)


@pytest.mark.parametrize(
    "candidate_other, is_expected_member, start_time, end_time, tzinfo, days_applied",
    [
        (  # 0. naive candidate time, naive start and end with provided tzinfo
            time(12, 30),
            False,
            time(12),
            time(13),
            GENERIC_TZ,
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
        (  # 1. naive candidate time, aware start and end; no provided tzinfo required
            time(12, 30),
            False,
            time(12, tzinfo=GENERIC_TZ),
            time(13, tzinfo=GENERIC_TZ),
            None,
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
        (  # 2. aware candidate time, naive start and end with provided tzinfo
            time(12, 30, tzinfo=GENERIC_TZ),
            True,
            time(12),
            time(13),
            GENERIC_TZ,
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
        (  # 3. aware candidate time, naive start and end with provided tzinfo
            time(12, 30, tzinfo=timezone(offset=timedelta(hours=3))),
            False,
            time(12),
            time(13),
            GENERIC_TZ,
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
        (  # 4. aware candidate time, aware start and naive end with provided tzinfo
            time(12, 30, tzinfo=GENERIC_TZ),
            True,
            time(12, tzinfo=GENERIC_TZ),
            time(13),
            GENERIC_TZ,
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
        (  # 5. aware candidate time, naive start and aware end with provided tzinfo
            time(12, 30, tzinfo=GENERIC_TZ),
            True,
            time(12),
            time(13, tzinfo=GENERIC_TZ),
            GENERIC_TZ,
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
        (  # 6. aware candidate time, aware start and end; no provided tzinfo required
            time(12, 30, tzinfo=GENERIC_TZ),
            True,
            time(12, tzinfo=GENERIC_TZ),
            time(13, tzinfo=GENERIC_TZ),
            None,
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
        (  # 7. AppliedInterval is right-open, so this will fail
            time(13, 0, tzinfo=GENERIC_TZ),
            False,
            time(12, tzinfo=GENERIC_TZ),
            time(13, tzinfo=GENERIC_TZ),
            None,
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
        (  # 8. AppliedInterval is right-open, so this will fail
            time(12, 0, tzinfo=GENERIC_TZ),
            False,
            time(13, tzinfo=GENERIC_TZ),
            time(12, tzinfo=GENERIC_TZ),
            None,
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
        (  # 9. start == end, we assume interval is 24-hours long (still valid, as interval is right-open)
            # any candidate time is thus in the interval (provided it has required tzinfo)
            time(12, 0, tzinfo=GENERIC_TZ),
            True,
            time(12, tzinfo=GENERIC_TZ),
            time(12, tzinfo=GENERIC_TZ),
            None,
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
        (  # 10. As above, but without tzinfo
            time(12, 0),
            False,
            time(12, tzinfo=GENERIC_TZ),
            time(12, tzinfo=GENERIC_TZ),
            None,
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
    ],
)
def test_applied_interval_time_membership(
    candidate_other: time,
    is_expected_member: bool,
    start_time: time,
    end_time: time,
    tzinfo: timezone,
    days_applied: DaysApplied,
) -> None:
    """"""

    ref_intvl = AppliedInterval(start_time=start_time, end_time=end_time, days_applied=days_applied, tzinfo=tzinfo)
    assert (candidate_other in ref_intvl) is is_expected_member


@pytest.mark.parametrize(
    "candidate_other, is_expected_member, start_time, end_time, tzinfo, days_applied",
    [
        # 2023/1/2 is a Monday, so this should return True
        (
            date(2023, 1, 2),
            True,
            time(12),
            time(13),
            GENERIC_TZ,
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
        (
            date(2023, 1, 1),
            False,
            time(12),
            time(13),
            GENERIC_TZ,
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
        (
            date(2023, 1, 1),
            True,
            time(12),
            time(13),
            GENERIC_TZ,
            DaysApplied(day_types=(DayType.HOLIDAYS,), holidays=country_holidays("AUS", subdiv="ACT", years=2020)),
        ),
        (
            date(2023, 1, 2),
            False,
            time(12),
            time(13),
            GENERIC_TZ,
            DaysApplied(day_types=(DayType.BUSINESS_DAYS,), holidays=country_holidays("AUS", subdiv="ACT", years=2020)),
        ),
    ],
)
def test_applied_interval_date_membership(
    candidate_other: time,
    is_expected_member: bool,
    start_time: time,
    end_time: time,
    tzinfo: timezone,
    days_applied: DaysApplied,
) -> None:
    """"""

    ref_intvl = AppliedInterval(start_time=start_time, end_time=end_time, days_applied=days_applied, tzinfo=tzinfo)
    assert (candidate_other in ref_intvl) is is_expected_member


@pytest.mark.parametrize(
    "candidate_other, is_expected_member, start_time, end_time, tzinfo, days_applied",
    [
        # 2023/1/2 is a Monday and the AppliedInterval is defined over [1200, 1300),
        # so this should return True
        (
            datetime(2023, 1, 2, 12, 30, 0, tzinfo=GENERIC_TZ),
            True,
            time(12),
            time(13),
            GENERIC_TZ,
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
        # 2023/1/2 is a Monday and the AppliedInterval is defined over [1200, 1300),
        # so this should return True
        (
            datetime(2023, 1, 2, 12, 0, 0, tzinfo=GENERIC_TZ),
            True,
            time(12),
            time(13),
            GENERIC_TZ,
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
        # 2023/1/2 is a Monday and the AppliedInterval is defined over [1200, 1300),
        # so this should return False
        (
            datetime(2023, 1, 2, 13, 0, 0, tzinfo=GENERIC_TZ),
            False,
            time(12),
            time(13),
            GENERIC_TZ,
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
        # Other is naive, so this should return False
        (
            datetime(2023, 1, 2, 12, 30, 0, tzinfo=None),
            False,
            time(12),
            time(13),
            GENERIC_TZ,
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
        # 2023/1/2 is a Monday and the AppliedInterval is defined over [1200, 1300),
        # so this should return False
        (
            datetime(2023, 1, 2, 12, 30, 0, tzinfo=GENERIC_TZ),
            False,
            time(12),
            time(13),
            GENERIC_TZ,
            DaysApplied(day_types=(DayType.TUESDAY,)),
        ),
        # 2023/1/2 is a holiday in AUS and the AppliedInterval is defined over [1200, 1300),
        # so this should return True
        (
            datetime(2023, 1, 2, 12, 30, 0, tzinfo=GENERIC_TZ),
            True,
            time(12),
            time(13),
            GENERIC_TZ,
            DaysApplied(day_types=(DayType.TUESDAY, DayType.HOLIDAYS), holidays=country_holidays("AUS", years=2020)),
        ),
    ],
)
def test_applied_interval_datetime_membership(
    candidate_other: datetime,
    is_expected_member: bool,
    start_time: time,
    end_time: time,
    tzinfo: timezone,
    days_applied: DaysApplied,
) -> None:
    """"""

    ref_intvl = AppliedInterval(start_time=start_time, end_time=end_time, days_applied=days_applied, tzinfo=tzinfo)
    assert (candidate_other in ref_intvl) is is_expected_member


@pytest.mark.parametrize(
    "interval_1, interval_2, expected_intersection",
    [
        (  # identity intersection
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
            AppliedInterval(
                start_time=time(6),
                end_time=time(7),
                days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
                tzinfo=ZoneInfo("Australia/Brisbane"),
            ),
        ),
        (  # no intersection in day_type, intersection in time => no intersection
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
            AppliedInterval(
                start_time=None,
                end_time=None,
                days_applied=DaysApplied(day_types=None),
                tzinfo=ZoneInfo("Australia/Brisbane"),
            ),
        ),
        (  # no intersection in day_type, partial intersection in time
            AppliedInterval(
                start_time=time(6),
                end_time=time(7),
                days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
                tzinfo=ZoneInfo("Australia/Brisbane"),
            ),
            AppliedInterval(
                start_time=time(6, 30),
                end_time=time(7),
                days_applied=DaysApplied(day_types=(DayType.TUESDAY,)),
                tzinfo=ZoneInfo("Australia/Brisbane"),
            ),
            AppliedInterval(
                start_time=None,
                end_time=None,
                days_applied=DaysApplied(day_types=None),
                tzinfo=ZoneInfo("Australia/Brisbane"),
            ),
        ),
        (  # intersection in day_type, partial intersection in time
            AppliedInterval(
                start_time=time(6),
                end_time=time(7),
                days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
                tzinfo=ZoneInfo("Australia/Brisbane"),
            ),
            AppliedInterval(
                start_time=time(6, 30),
                end_time=time(7),
                days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
                tzinfo=ZoneInfo("Australia/Brisbane"),
            ),
            AppliedInterval(
                start_time=time(6, 30),
                end_time=time(7),
                days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
                tzinfo=ZoneInfo("Australia/Brisbane"),
            ),
        ),
        (  # no intersection at right-open edges iff no day type intersection
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
            AppliedInterval(
                start_time=None,
                end_time=None,
                days_applied=DaysApplied(day_types=None),
                tzinfo=ZoneInfo("Australia/Brisbane"),
            ),
        ),
    ],
)
def test_applied_interval_intersection(interval_1, interval_2, expected_intersection):
    """"""
    assert (interval_1 & interval_2) == expected_intersection
