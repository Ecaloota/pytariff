from enum import Enum, auto
from typing import Collection

## PART OF REFACTOR -> DONE


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

    @staticmethod
    def _weekdays() -> list["DayType"]:
        return [
            DayType.MONDAY,
            DayType.TUESDAY,
            DayType.WEDNESDAY,
            DayType.THURSDAY,
            DayType.FRIDAY,
        ]

    @staticmethod
    def _weekends() -> list["DayType"]:
        return [DayType.SATURDAY, DayType.SUNDAY]

    def __and__(self, other: "DayType") -> Collection["DayType"]:
        """
        General Rules about DayType intersections:
            0. DayType.X & DayType.Y => DayType.Y & DayType.X
            1. DayType.X & DayType.X = {DayType.X}
            2. DayType.X & DayType.ALL_DAYS = {DayType.X}
            3. DayType.WEEKDAYS & DayType.WEEKENDS = {}

        Examples:
        DayType.MONDAY & DayType.TUESDAY = {}
        DayType.MONDAY & DayType.ALL_DAYS = {DayType.MONDAY}
        DayType.MONDAY & DayType.MONDAY = {DayType.MONDAY}
        """

        weekday_intersection = [self, DayType.ALL_DAYS, DayType.WEEKDAYS]
        weekend_intersection = [self, DayType.ALL_DAYS, DayType.WEEKENDS]

        match self:
            case (
                DayType.MONDAY
                | DayType.TUESDAY
                | DayType.WEDNESDAY
                | DayType.THURSDAY
                | DayType.FRIDAY
            ):
                return {self} if other in weekday_intersection else {}

            case DayType.SATURDAY | DayType.SUNDAY:
                return {self} if other in weekend_intersection else {}

            case DayType.WEEKDAYS:
                if other in [self, DayType.ALL_DAYS]:
                    return {self}
                elif other in DayType._weekdays():
                    return {other}
                else:
                    return {}

            case DayType.WEEKENDS:
                if other in [self, DayType.ALL_DAYS]:
                    return {self}
                elif other in DayType._weekends():
                    return {other}
                else:
                    return {}

            case DayType.ALL_DAYS:
                return {other}
