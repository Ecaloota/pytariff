import pytest

from utal._internal.day_type import DayType


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
