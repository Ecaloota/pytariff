from datetime import date, datetime
from typing import Optional
import pytest

from holidays import HolidayBase, country_holidays
from utal.core.day import DayType, DaysApplied


@pytest.mark.parametrize(
    "member",
    [
        DayType.MONDAY,
        DayType.TUESDAY,
        DayType.WEDNESDAY,
        DayType.THURSDAY,
        DayType.FRIDAY,
        DayType.SATURDAY,
        DayType.SUNDAY,
        DayType.BUSINESS_DAYS,
        DayType.HOLIDAYS,
        DayType.ALL_DAYS,
    ],
)
def test_day_type_membership(member):
    assert member in DayType


@pytest.mark.parametrize(
    "day_type_a, day_type_b, intersection",
    [
        # Any day intersection with ALL_DAYS is itself
        (DayType.MONDAY, DayType.ALL_DAYS, {DayType.MONDAY}),
        (DayType.TUESDAY, DayType.ALL_DAYS, {DayType.TUESDAY}),
        (DayType.WEDNESDAY, DayType.ALL_DAYS, {DayType.WEDNESDAY}),
        (DayType.THURSDAY, DayType.ALL_DAYS, {DayType.THURSDAY}),
        (DayType.FRIDAY, DayType.ALL_DAYS, {DayType.FRIDAY}),
        (DayType.SATURDAY, DayType.ALL_DAYS, {DayType.SATURDAY}),
        (DayType.SUNDAY, DayType.ALL_DAYS, {DayType.SUNDAY}),
        (DayType.WEEKDAYS, DayType.ALL_DAYS, {DayType.WEEKDAYS}),
        (DayType.WEEKENDS, DayType.ALL_DAYS, {DayType.WEEKENDS}),
        (DayType.BUSINESS_DAYS, DayType.ALL_DAYS, {DayType.BUSINESS_DAYS}),
        (DayType.HOLIDAYS, DayType.ALL_DAYS, {DayType.HOLIDAYS}),
        # Any self intersection is self
        (DayType.MONDAY, DayType.MONDAY, {DayType.MONDAY}),
        (DayType.TUESDAY, DayType.TUESDAY, {DayType.TUESDAY}),
        (DayType.WEDNESDAY, DayType.WEDNESDAY, {DayType.WEDNESDAY}),
        (DayType.THURSDAY, DayType.THURSDAY, {DayType.THURSDAY}),
        (DayType.FRIDAY, DayType.FRIDAY, {DayType.FRIDAY}),
        (DayType.SATURDAY, DayType.SATURDAY, {DayType.SATURDAY}),
        (DayType.SUNDAY, DayType.SUNDAY, {DayType.SUNDAY}),
        (DayType.WEEKDAYS, DayType.WEEKDAYS, {DayType.WEEKDAYS}),
        (DayType.WEEKENDS, DayType.WEEKENDS, {DayType.WEEKENDS}),
        (DayType.ALL_DAYS, DayType.ALL_DAYS, {DayType.ALL_DAYS}),
        (DayType.BUSINESS_DAYS, DayType.BUSINESS_DAYS, {DayType.BUSINESS_DAYS}),
        (DayType.HOLIDAYS, DayType.HOLIDAYS, {DayType.HOLIDAYS}),
        # MONDAY intersects with the following
        # See comments in DayType.__and__ for rationale for intersection with BUSINESS_DAYS and HOLIDAYS
        (DayType.MONDAY, DayType.WEEKDAYS, {DayType.MONDAY}),
        (DayType.MONDAY, DayType.BUSINESS_DAYS, {DayType.MONDAY}),
        (DayType.MONDAY, DayType.HOLIDAYS, {DayType.MONDAY}),
        # MONDAY does not intersect with the following
        (DayType.MONDAY, DayType.TUESDAY, {}),
        (DayType.MONDAY, DayType.WEDNESDAY, {}),
        (DayType.MONDAY, DayType.THURSDAY, {}),
        (DayType.MONDAY, DayType.FRIDAY, {}),
        (DayType.MONDAY, DayType.SATURDAY, {}),
        (DayType.MONDAY, DayType.SUNDAY, {}),
        (DayType.MONDAY, DayType.WEEKENDS, {}),
        # TUESDAY intersects with the following
        # See comments in DayType.__and__ for rationale for intersection with BUSINESS_DAYS and HOLIDAYS
        (DayType.TUESDAY, DayType.WEEKDAYS, {DayType.TUESDAY}),
        (DayType.TUESDAY, DayType.BUSINESS_DAYS, {DayType.TUESDAY}),
        (DayType.TUESDAY, DayType.HOLIDAYS, {DayType.TUESDAY}),
        # TUESDAY does not intersect with the following
        (DayType.TUESDAY, DayType.MONDAY, {}),
        (DayType.TUESDAY, DayType.WEDNESDAY, {}),
        (DayType.TUESDAY, DayType.THURSDAY, {}),
        (DayType.TUESDAY, DayType.FRIDAY, {}),
        (DayType.TUESDAY, DayType.SATURDAY, {}),
        (DayType.TUESDAY, DayType.SUNDAY, {}),
        (DayType.TUESDAY, DayType.WEEKENDS, {}),
        # WEDNESDAY intersects with the following
        # See comments in DayType.__and__ for rationale for intersection with BUSINESS_DAYS and HOLIDAYS
        (DayType.WEDNESDAY, DayType.WEEKDAYS, {DayType.WEDNESDAY}),
        (DayType.WEDNESDAY, DayType.BUSINESS_DAYS, {DayType.WEDNESDAY}),
        (DayType.WEDNESDAY, DayType.HOLIDAYS, {DayType.WEDNESDAY}),
        # WEDNESDAY does not intersect with the following
        (DayType.WEDNESDAY, DayType.MONDAY, {}),
        (DayType.WEDNESDAY, DayType.TUESDAY, {}),
        (DayType.WEDNESDAY, DayType.THURSDAY, {}),
        (DayType.WEDNESDAY, DayType.FRIDAY, {}),
        (DayType.WEDNESDAY, DayType.SATURDAY, {}),
        (DayType.WEDNESDAY, DayType.SUNDAY, {}),
        (DayType.WEDNESDAY, DayType.WEEKENDS, {}),
        # THURSDAY intersects with the following
        # See comments in DayType.__and__ for rationale for intersection with BUSINESS_DAYS and HOLIDAYS
        (DayType.THURSDAY, DayType.WEEKDAYS, {DayType.THURSDAY}),
        (DayType.THURSDAY, DayType.BUSINESS_DAYS, {DayType.THURSDAY}),
        (DayType.THURSDAY, DayType.HOLIDAYS, {DayType.THURSDAY}),
        # THURSDAY does not intersect with the following
        (DayType.THURSDAY, DayType.MONDAY, {}),
        (DayType.THURSDAY, DayType.TUESDAY, {}),
        (DayType.THURSDAY, DayType.WEDNESDAY, {}),
        (DayType.THURSDAY, DayType.FRIDAY, {}),
        (DayType.THURSDAY, DayType.SATURDAY, {}),
        (DayType.THURSDAY, DayType.SUNDAY, {}),
        (DayType.THURSDAY, DayType.WEEKENDS, {}),
        # FRIDAY intersects with the following
        # See comments in DayType.__and__ for rationale for intersection with BUSINESS_DAYS and HOLIDAYS
        (DayType.FRIDAY, DayType.WEEKDAYS, {DayType.FRIDAY}),
        (DayType.FRIDAY, DayType.BUSINESS_DAYS, {DayType.FRIDAY}),
        (DayType.FRIDAY, DayType.HOLIDAYS, {DayType.FRIDAY}),
        # FRIDAY does not intersect with the following
        (DayType.FRIDAY, DayType.MONDAY, {}),
        (DayType.FRIDAY, DayType.TUESDAY, {}),
        (DayType.FRIDAY, DayType.WEDNESDAY, {}),
        (DayType.FRIDAY, DayType.THURSDAY, {}),
        (DayType.FRIDAY, DayType.SATURDAY, {}),
        (DayType.FRIDAY, DayType.SUNDAY, {}),
        (DayType.FRIDAY, DayType.WEEKENDS, {}),
        # SATURDAY intersects with the following
        # See comments in DayType.__and__ for rationale for intersection with BUSINESS_DAYS and HOLIDAYS
        (DayType.SATURDAY, DayType.WEEKENDS, {DayType.SATURDAY}),
        (DayType.SATURDAY, DayType.BUSINESS_DAYS, {DayType.SATURDAY}),
        (DayType.SATURDAY, DayType.HOLIDAYS, {DayType.SATURDAY}),
        # SATURDAY does not intersect with the following
        (DayType.SATURDAY, DayType.MONDAY, {}),
        (DayType.SATURDAY, DayType.TUESDAY, {}),
        (DayType.SATURDAY, DayType.WEDNESDAY, {}),
        (DayType.SATURDAY, DayType.THURSDAY, {}),
        (DayType.SATURDAY, DayType.FRIDAY, {}),
        (DayType.SATURDAY, DayType.SUNDAY, {}),
        (DayType.SATURDAY, DayType.WEEKDAYS, {}),
        # SUNDAY intersects with the following
        # See comments in DayType.__and__ for rationale for intersection with BUSINESS_DAYS and HOLIDAYS
        (DayType.SUNDAY, DayType.WEEKENDS, {DayType.SUNDAY}),
        (DayType.SUNDAY, DayType.BUSINESS_DAYS, {DayType.SUNDAY}),
        (DayType.SUNDAY, DayType.HOLIDAYS, {DayType.SUNDAY}),
        # SUNDAY does not intersect with the following
        (DayType.SUNDAY, DayType.MONDAY, {}),
        (DayType.SUNDAY, DayType.TUESDAY, {}),
        (DayType.SUNDAY, DayType.WEDNESDAY, {}),
        (DayType.SUNDAY, DayType.THURSDAY, {}),
        (DayType.SUNDAY, DayType.FRIDAY, {}),
        (DayType.SUNDAY, DayType.SATURDAY, {}),
        (DayType.SUNDAY, DayType.WEEKDAYS, {}),
        # BUSINESS_DAYS do not intersect with HOLIDAYS
        (DayType.BUSINESS_DAYS, DayType.HOLIDAYS, {}),
    ],
)
def test_day_type_intersections(day_type_a: DayType, day_type_b: DayType, intersection: set[DayType]) -> None:
    """"""

    assert day_type_a & day_type_b == intersection


def no_day_type_holidays(t: DayType) -> HolidayBase:
    """Generate an instance of pre-computed AUS HolidayBase for 2020,
    removing those dates which would match the given DayType.
    We do this so that we can test what happens under that scenario in
    DaysApplied intersections.
    """

    custom_holidays = country_holidays("AUS", years=2020)
    custom_holidays_keys = [k for k in custom_holidays.keys()]
    for k in custom_holidays_keys:
        if DayType[k.strftime("%A").upper()] == t:
            custom_holidays.pop(k)

    return custom_holidays


@pytest.mark.parametrize(
    "day_types, holidays",
    [
        (  # Basic setup
            (DayType.MONDAY,),
            None,
        ),
        (  # Overlap in DayType is allowed
            (DayType.MONDAY, DayType.MONDAY),
            None,
        ),
        (  # Overlap in DayType is allowed
            (DayType.MONDAY, DayType.ALL_DAYS),
            None,
        ),
        (  # If BUSINESS_DAYS or HOLIDAYS are used, holidays is a required arg
            (DayType.BUSINESS_DAYS,),
            country_holidays("AUS", years=2020),
        ),
        (  # If BUSINESS_DAYS or HOLIDAYS are used, holidays is a required arg
            (DayType.HOLIDAYS,),
            country_holidays("AUS", years=2020),
        ),
    ],
)
def test_days_applied_valid_construction(day_types: tuple[DayType, ...], holidays: Optional[HolidayBase]):
    """"""

    assert DaysApplied(day_types=day_types, holidays=holidays)


@pytest.mark.parametrize(
    "day_types, holidays",
    [
        (  # If BUSINESS_DAYS or HOLIDAYS are used, holidays is a required arg
            (DayType.MONDAY, DayType.BUSINESS_DAYS),
            None,
        ),
        (  # If BUSINESS_DAYS or HOLIDAYS are used, holidays is a required arg
            (DayType.BUSINESS_DAYS,),
            None,
        ),
        (  # If BUSINESS_DAYS or HOLIDAYS are used, holidays is a required arg
            (DayType.HOLIDAYS,),
            None,
        ),
    ],
)
def test_days_applied_invalid_construction(day_types: tuple[DayType, ...], holidays: Optional[HolidayBase]):
    """"""

    with pytest.raises(ValueError):
        DaysApplied(day_types=day_types, holidays=holidays)


@pytest.mark.parametrize(
    "candidate_other, is_expected_member, days_applied_instance",
    [
        (  # 0. 1/1/2023 is a Sunday
            datetime(2023, 1, 1),
            True,
            DaysApplied(day_types=(DayType.SUNDAY,)),
        ),
        (  # 1. 1/1/2023 is a Sunday
            datetime(2023, 1, 1),
            False,
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
        (  # 2. All days are in the ALL_DAYS type
            datetime(2023, 1, 1),
            True,
            DaysApplied(day_types=(DayType.ALL_DAYS,)),
        ),
        (  # 3. Sunday is not in WEEKDAYS
            datetime(2023, 1, 1),
            False,
            DaysApplied(day_types=(DayType.WEEKDAYS,)),
        ),
        (  # 4. Monday is in WEEKDAYS
            datetime(2023, 1, 2),
            True,
            DaysApplied(day_types=(DayType.WEEKDAYS,)),
        ),
        (  # 5. Monday is in WEEKDAYS (even though it's not in WEEKENDS, which is also there)
            datetime(2023, 1, 2),
            True,
            DaysApplied(day_types=(DayType.WEEKDAYS, DayType.WEEKENDS)),
        ),
        (  # 6. Sunday is in WEEKENDS
            datetime(2023, 1, 1),
            True,
            DaysApplied(day_types=(DayType.WEEKENDS,)),
        ),
        (  # 7. New Years Day is in HOLIDAYS (for given HolidayBase instance)
            datetime(2023, 1, 1),
            True,
            DaysApplied(day_types=(DayType.HOLIDAYS,), holidays=country_holidays("AUS", years=2020)),
        ),
        (  # 8. New Years Day is not in BUSINESS_DAYS (for given HolidayBase instance)
            datetime(2023, 1, 1),
            False,
            DaysApplied(day_types=(DayType.BUSINESS_DAYS,), holidays=country_holidays("AUS", years=2020)),
        ),
    ],
)
def test_days_applied_membership_valid_input(
    candidate_other: date | datetime, is_expected_member: bool, days_applied_instance: DaysApplied
) -> None:
    """"""

    assert (candidate_other in days_applied_instance) is is_expected_member


# TODO there are more tests to enumerate here
@pytest.mark.parametrize(
    "candidate_other, days_applied_instance, expected_intersection",
    [
        (
            DaysApplied(day_types=(DayType.MONDAY,)),
            DaysApplied(day_types=(DayType.MONDAY,)),
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
        (
            DaysApplied(day_types=(DayType.MONDAY,)),
            DaysApplied(day_types=(DayType.TUESDAY,)),
            DaysApplied(),
        ),
        (  # this returns an intersection because there is no intersection between holidays
            DaysApplied(day_types=(DayType.MONDAY,)),
            DaysApplied(day_types=(DayType.HOLIDAYS,), holidays=country_holidays("AUS", years=2020)),
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
        (  # this returns an intersection because there is a holiday on a Monday in Aus/2020
            DaysApplied(day_types=(DayType.MONDAY,), holidays=country_holidays("AUS", years=2020)),
            DaysApplied(day_types=(DayType.HOLIDAYS,), holidays=country_holidays("AUS", years=2020)),
            DaysApplied(day_types=(DayType.MONDAY,)),
        ),
        (  # this returns NO (day_types) intersection because there are no holidays on a Monday in this HolidayBase
            DaysApplied(day_types=(DayType.MONDAY,), holidays=country_holidays("AUS", years=2020)),
            DaysApplied(day_types=(DayType.HOLIDAYS,), holidays=no_day_type_holidays(DayType.MONDAY)),
            DaysApplied(),
        ),
    ],
)
def test_days_applied_intersection(
    candidate_other: DaysApplied, days_applied_instance: DaysApplied, expected_intersection: DaysApplied
):
    """"""

    assert (candidate_other & days_applied_instance).day_types_equal(expected_intersection)
