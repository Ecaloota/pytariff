from enum import Enum, auto
from typing import Collection


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
