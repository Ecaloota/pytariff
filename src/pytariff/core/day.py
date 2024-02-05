from datetime import date, datetime
from enum import Enum, auto
from typing import Collection
from holidays import HolidayBase

from pydantic import BaseModel, ConfigDict, model_validator

from pytariff._internal import helper


class DayType(Enum):
    MONDAY = auto()
    TUESDAY = auto()
    WEDNESDAY = auto()
    THURSDAY = auto()
    FRIDAY = auto()
    SATURDAY = auto()
    SUNDAY = auto()

    # custom logic required for these
    WEEKDAYS = auto()
    WEEKENDS = auto()
    ALL_DAYS = auto()
    BUSINESS_DAYS = auto()
    HOLIDAYS = auto()

    def __contains__(self, value: object) -> bool:
        """For our purposes, a given value is in self iff the value and self are equal.
        This is implemented so we can run comparisons like (DayType.BUSINESS_DAYS in self.day_types) when both
        self.day_types is a typle of DayType or an instance thereof.
        """
        return self == value

    def __and__(self, other: "DayType") -> Collection["DayType"]:
        """
        General Rules about DayType intersections:
            1. DayType.X & DayType.ALL_DAYS = {DayType.X}
            2. DayType.HOLIDAYS & DayType.BUSINESS_DAYS = {}
            2. DayType.WEEKDAYS & DayType.WEEKENDS = {}

        Examples:
        DayType.MONDAY & DayType.TUESDAY = {}
        DayType.MONDAY & DayType.ALL_DAYS = {DayType.MONDAY}
        DayType.MONDAY & DayType.MONDAY = {DayType.MONDAY}

        NOTE that in the general case, a MONDAY could be a BUSINESS_DAY or a HOLIDAY, so the following
        intersections hold. Compare this behaviour with the intersection of DayTypes in a pair of DaysApplied.day_types
        DayType.MONDAY & DayType.BUSINESS_DAYS = {DayType.MONDAY}
        DayType.MONDAY & DayType.HOLIDAYS = {DayType.MONDAY}

        NOTE using similar logic to above, the following intersection holds. For this intersection
        to be non-empty, BUSINESS_DAYS would need to at least be a superset of WEEKDAYS
        (all weekdays would need to be business days).
        DayType.WEEKDAYS & DayType.BUSINESS_DAYS = {}

        NOTE Some businesses may consider WEEKENDS to be a subset of BUSINESS_DAYS, (e.g. churches),
        so in the general case:
        DayType.SATURDAY & DayType.BUSINESS_DAYS = {DayType.SATURDAY}
        DayType.SUNDAY & DayType.BUSINESS_DAYS = {DayType.SUNDAY}
        """

        weekday_intersection = [self, DayType.ALL_DAYS, DayType.WEEKDAYS, DayType.BUSINESS_DAYS, DayType.HOLIDAYS]
        weekend_intersection = [self, DayType.ALL_DAYS, DayType.WEEKENDS, DayType.BUSINESS_DAYS, DayType.HOLIDAYS]

        match self:
            case DayType.MONDAY | DayType.TUESDAY | DayType.WEDNESDAY | DayType.THURSDAY | DayType.FRIDAY:
                return {self} if other in weekday_intersection else {}

            case DayType.SATURDAY | DayType.SUNDAY:
                return {self} if other in weekend_intersection else {}

            case DayType.WEEKDAYS:
                return {self} if other in [self, DayType.ALL_DAYS] else {}

            case DayType.WEEKENDS:
                return {self} if other in [self, DayType.ALL_DAYS] else {}

            case DayType.ALL_DAYS:
                return {self} if other in [self] else {}

            case DayType.BUSINESS_DAYS:
                return {self} if other in [self, DayType.ALL_DAYS] else {}

            case DayType.HOLIDAYS:
                return {self} if other in [self, DayType.ALL_DAYS] else {}


class DaysApplied(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    day_types: tuple[DayType, ...] | DayType | None = None
    holidays: HolidayBase | None = None

    @model_validator(mode="after")
    def validate_holidays_present_if_day_type_business_days(self) -> "DaysApplied":
        if self.day_types is not None:
            if (DayType.BUSINESS_DAYS in self.day_types) and (self.holidays is None or self.holidays.years == set()):
                raise ValueError
        return self

    @model_validator(mode="after")
    def validate_holidays_present_if_day_type_holidays(self) -> "DaysApplied":
        if self.day_types is not None:
            if DayType.HOLIDAYS in self.day_types and (self.holidays is None or self.holidays.years == set()):
                raise ValueError
        return self

    def __contains__(self, other: date | datetime) -> bool:  # noqa[C901]
        """
        Returns True if other is deemed to exist within any of the day_type categories passed
        at instantiation.

        If DayType.BUSINESS_DAYS or DayType.HOLIDAYS in self.day_types, a holidays.HolidayBase instance
        must be passed at instantiation.
        """

        if not (helper.is_datetime_type(other) or helper.is_date_type(other)):
            raise ValueError

        if self.day_types is None:
            return False

        # always return True if ALL_DAYS is passed
        if DayType.ALL_DAYS in self.day_types:
            return True

        if DayType.WEEKDAYS in self.day_types:
            if DayType[other.strftime("%A").upper()] in [
                DayType.MONDAY,
                DayType.TUESDAY,
                DayType.WEDNESDAY,
                DayType.THURSDAY,
                DayType.FRIDAY,
            ]:
                return True

        if DayType.WEEKENDS in self.day_types:
            if DayType[other.strftime("%A").upper()] in [DayType.SATURDAY, DayType.SUNDAY]:
                return True

        # Determine whether other is a business day (i.e. not a holiday).
        # If it is, return True, else keep going.
        if DayType.BUSINESS_DAYS in self.day_types:
            if other not in self.holidays:  # type: ignore # holidays cannot be none after instantiation
                return True

        if DayType.HOLIDAYS in self.day_types:
            if other in self.holidays:  # type: ignore # holidays cannot be none after instantiation
                return True

        return DayType[other.strftime("%A").upper()] in self.day_types

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DaysApplied):
            raise NotImplementedError
        return self.day_types == other.day_types and self.holidays == other.holidays

    def __hash__(self) -> int:
        return hash(self.day_types)  # TODO this is not strictly correct, but avoids hashing of external library objs

    def day_types_equal(self, other: object) -> bool:
        """A weaker assertion of equality, for when equality between holidays is not important"""
        if not isinstance(other, DaysApplied):
            raise NotImplementedError
        return self.day_types == other.day_types

    def __and__(self, other: "DaysApplied") -> "DaysApplied":  # noqa
        """The intersection between two DaysApplied objects is the set of all intersections
        between all elements of self.day_types and other.day_types EXCEPT that intersections
        between any two DayTypes where at least one DayType is in
        [DayType.BUSINESS_DAYS, DayType.HOLIDAYS] are verified to be intersections with
        reference to the holidays in self.holidays iff self.holidays is not None.

        This will yield divergent behaviour relative to the set intersections of DayTypes.

        Specifically for example, this condition means that while, in the general case:
            DayType.MONDAY & DayType.HOLIDAYS = {DayType.MONDAY}

        For the specific case where (self.holidays & other.holidays) is not None and yet did not contain any holiday
        that occurred on a Monday, and where self.day_types = (DayType.MONDAY,),
        and other.day_types = (DayType.HOLIDAYS,) the intersection would correctly be:
            self.day_types & other.day_types = {}

        With similar outcomes for intersections with DayType.BUSINESS_DAYS. If a given interval
        needs to exclude a day from its definition of a BUSINESS_DAY (for example, a particular
        business takes a day-off that is not a recognised holiday), this day can be added to the
        self.holidays list manually, and thus prevent any unintended intersections.

        General Rules:
        1. If DayType.ALL_DAYS is present in either self or other, the intersection is the
            unique set of the union of self and other (before accounting for business days and holidays)
        2. If there is any intersection between self and other, we keep the intersection of
            self.holidays and other.holidays.
        """

        if self.holidays is None or other.holidays is None:
            holiday_intersection_keys = None
            holiday_intersection = None
        else:
            holiday_intersection_keys = self.holidays.keys() & other.holidays.keys()
            holiday_intersection = HolidayBase()
            holiday_intersection.append([k for k in holiday_intersection_keys])

        if self.day_types is None or other.day_types is None:
            return DaysApplied(day_types=None, holidays=holiday_intersection)

        def _xor_eq(a: DayType, b: DayType, d: DayType) -> bool:
            return (a == d and b != d) or (b == d and a != d)

        def _one_day_is_type(t: DayType) -> bool:
            return _xor_eq(day_type, other_day, t)

        def _no_day_is_type(t: DayType) -> bool:
            return day_type != t and other_day != t

        def _is_holiday_intersection_check_required(inter: set) -> bool:
            return (
                holiday_intersection_keys is not None
                and (_one_day_is_type(DayType.BUSINESS_DAYS) or _one_day_is_type(DayType.HOLIDAYS))
                and _no_day_is_type(DayType.ALL_DAYS)
                and inter != set()
            )

        def _day_type_in_holidays(t: DayType) -> bool:
            """A given DayType is in self.holidays iff any day in holidays is recognised as a matching DayType
            In practice, this will only catch MONDAY through SUNDAY unless we also define a mapping from an arbitrary
            holiday to other DayTypes.
            """

            if holiday_intersection_keys is None:
                raise ValueError

            for holiday_date in holiday_intersection_keys:
                if DayType[holiday_date.strftime("%A").upper()] == t:
                    return True
                # extra mappings would go here
            return False

        intersections: set[DayType] = set()
        if not isinstance(self.day_types, tuple):
            self.day_types = (self.day_types,)
        if not isinstance(other.day_types, tuple):
            other.day_types = (other.day_types,)

        for day_type in self.day_types:
            for other_day in other.day_types:
                inter = day_type & other_day

                if _is_holiday_intersection_check_required(inter):  # type: ignore  # probably an issue TODO
                    d = list(inter)[0]
                    # Check if named day is present in self.holidays. If not present, inter = {}, else pass
                    if _one_day_is_type(DayType.HOLIDAYS) and not _day_type_in_holidays(d):
                        inter = {}
                    # Check if named day is NOT present in self.holidays. If not present, pass, else inter = {}
                    elif _one_day_is_type(DayType.BUSINESS_DAYS) and _day_type_in_holidays(d):
                        inter = {}

                intersections.update(inter)

        to_tuple = tuple(intersections) or None
        return DaysApplied(day_types=to_tuple, holidays=holiday_intersection)
