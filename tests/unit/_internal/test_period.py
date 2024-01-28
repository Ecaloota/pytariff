# from datetime import datetime
# import pytest

# from utal._internal.period import ResetPeriod


# @pytest.mark.parametrize(
#     "reset_period, from_datetime, to_days_expected",
#     [
#         (ResetPeriod.DAILY, datetime(2023, 1, 1, 6), "1D"),
#         (ResetPeriod.HOURLY, datetime(2023, 1, 1, 6), "1h"),
#         (ResetPeriod.FIRST_OF_MONTH, datetime(2023, 1, 1, 6), "31D"),
#         (ResetPeriod.FIRST_OF_QUARTER, datetime(2023, 1, 1, 6), "90D"),
#         (ResetPeriod.FIRST_OF_MONTH, datetime(2023, 1, 15, 6), "17D"),
#         (ResetPeriod.FIRST_OF_QUARTER, datetime(2023, 2, 15, 6), "45D"),
#         (ResetPeriod.FIRST_OF_MONTH, datetime(2023, 2, 1, 6), "28D"),  # non-leap year
#         (ResetPeriod.FIRST_OF_MONTH, datetime(2020, 2, 1, 6), "29D"),  # leap year
#     ],
# )
# def test_reset_period_to_days_method(reset_period: ResetPeriod, from_datetime: datetime, to_days_expected: str) -> None: # noqa
#     """Given some input datetime, return the number of days between it and the next FIRST_OF_MONTH,
#     FIRST_OF_QUARTER, or the string representation of the Enum value for other valid
#     ResetPeriod values"""

#     assert reset_period._to_days(_from=from_datetime) == to_days_expected
