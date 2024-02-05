from datetime import date, datetime, time, timezone
from typing import Optional, TypeGuard, TypeVar
from zoneinfo import ZoneInfo

T = TypeVar("T")


def is_date_type(obj: T) -> TypeGuard[date]:
    return isinstance(obj, date) and not isinstance(obj, datetime)


def is_datetime_type(obj: T) -> TypeGuard[datetime]:
    return not is_date_type(obj) and isinstance(obj, datetime)


def is_aware(obj: datetime | time) -> bool:
    if is_datetime_type(obj):
        return obj.tzinfo is not None and obj.utcoffset() is not None
    elif isinstance(obj, time):
        return obj.tzinfo is not None and obj.tzinfo.utcoffset(None) is not None

    return (is_datetime_type(obj) or isinstance(obj, time)) and obj.tzinfo is not None and obj.utcoffset() is not None


def is_naive(obj: datetime | time) -> bool:
    return not is_aware(obj)


def convert_to_aware_datetime(obj: datetime | date, tzinfo: Optional[timezone | ZoneInfo]) -> datetime:
    if is_date_type(obj):
        if tzinfo is None:
            raise ValueError
        obj = datetime.combine(date=obj, time=time(0, 0, 0), tzinfo=tzinfo)

    elif is_datetime_type(obj) and is_naive(obj):
        if tzinfo is None:
            raise ValueError
        obj = datetime.combine(date=obj.date(), time=obj.time(), tzinfo=tzinfo)

    elif is_datetime_type(obj):
        return obj

    else:
        raise ValueError

    return obj
