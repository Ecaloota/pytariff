from typing import Any
from zoneinfo import ZoneInfo
import pytest

from datetime import date, datetime, time

from utal._internal import helper


@pytest.mark.parametrize(
    "obj, is_date_type",
    [
        (date(2023, 1, 1), True),  # true date
        (datetime(2023, 1, 1, 12, 0, 0), False),  # datetime is not a date (for these purposes)
        (datetime(2023, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")), False),  # neither is naive datetime
        (time(12, 1, tzinfo=ZoneInfo("UTC")), False),  # time is not a date
        (time(12, 1), False),  # neither is a naive time
        ("2023, 1, 1", False),  # date-coercible is not a date
    ],
)
def test_helper_is_date_type(obj: Any, is_date_type: bool) -> None:
    assert helper.is_date_type(obj) is is_date_type


@pytest.mark.parametrize(
    "obj, is_datetime_type",
    [
        (date(2023, 1, 1), False),  # date is not a datetime (for these purposes)
        (datetime(2023, 1, 1, 12, 0, 0), True),  # true datetime
        (datetime(2023, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")), True),  # true tz-aware datetime
        (time(12, 1, tzinfo=ZoneInfo("UTC")), False),  # time is not a datetime
        (time(12, 1), False),  # neither is a naive time
        ("2023, 1, 1", False),  # datetime-coercible is not a datetime
    ],
)
def test_helper_is_datetime_type(obj: Any, is_datetime_type: bool) -> None:
    assert helper.is_datetime_type(obj) is is_datetime_type


@pytest.mark.parametrize(
    "obj, is_aware",
    [
        (date(2023, 1, 1), False),  # dates cannot be aware
        (datetime(2023, 1, 1, 12, 0, 0), False),  # naive datetime is not aware
        (datetime(2023, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")), True),  # true tz-aware datetime
        (time(12, 1, tzinfo=ZoneInfo("UTC")), True),  # true tz-aware time
        (time(12, 1), False),  # naive time is not aware
        ("12:00:00T00:00Z", False),  # aware time-coercible is not aware
    ],
)
def test_helper_is_aware(obj: Any, is_aware: bool) -> None:
    assert helper.is_aware(obj) is is_aware


@pytest.mark.parametrize(
    "obj, is_naive",
    [
        (date(2023, 1, 1), True),  # inverse of is_aware tests above
        (datetime(2023, 1, 1, 12, 0, 0), True),
        (datetime(2023, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC")), False),
        (time(12, 1, tzinfo=ZoneInfo("UTC")), False),
        (time(12, 1), True),
        ("12:00:00T00:00Z", True),
    ],
)
def test_helper_is_naive(obj: Any, is_naive: bool) -> None:
    assert helper.is_naive(obj) is is_naive


# TODO
def test_helper_convert_to_aware_datetime():
    pass
