from datetime import date, datetime
from typing import Optional

import pytest
from holidays import HolidayBase, country_holidays

from utal.schema.day_type import DayType
from utal.schema.days_applied import DaysApplied


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
