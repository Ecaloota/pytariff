from datetime import datetime
import pytest

from pytariff.core.reset import ResetPeriod


@pytest.mark.parametrize(
    "reset_period, until_datetime, ref_datetime, exp_num_occurences",
    [
        (ResetPeriod.DAILY, datetime(2023, 1, 1), datetime(2023, 1, 1), 1),
        (ResetPeriod.DAILY, datetime(2023, 1, 2), datetime(2023, 1, 1), 2),
        (ResetPeriod.FIRST_OF_MONTH, datetime(2023, 1, 5), datetime(2023, 1, 5), 1),
        (ResetPeriod.FIRST_OF_MONTH, datetime(2023, 1, 5), datetime(2023, 1, 2), 1),
        (ResetPeriod.FIRST_OF_MONTH, datetime(2023, 2, 2), datetime(2023, 1, 1), 2),
        (ResetPeriod.FIRST_OF_QUARTER, datetime(2023, 2, 2), datetime(2023, 2, 2), 1),
        (ResetPeriod.FIRST_OF_QUARTER, datetime(2023, 2, 2), datetime(2023, 1, 1), 1),
        (ResetPeriod.FIRST_OF_QUARTER, datetime(2023, 8, 2), datetime(2023, 1, 2), 3),
        (ResetPeriod.QUARTER_HOURLY, datetime(2023, 1, 1, 1), datetime(2023, 1, 1, 1), 1),
        (ResetPeriod.QUARTER_HOURLY, datetime(2023, 1, 1, 1), datetime(2023, 1, 1), 5),
        (ResetPeriod.QUARTER_HOURLY, datetime(2023, 1, 1, 2), datetime(2023, 1, 1), 9),
        (ResetPeriod.HALF_HOURLY, datetime(2023, 1, 1), datetime(2023, 1, 1), 1),
        (ResetPeriod.HALF_HOURLY, datetime(2023, 1, 1, 1), datetime(2023, 1, 1), 3),
        (ResetPeriod.HOURLY, datetime(2023, 1, 1), datetime(2023, 1, 1), 1),
        (ResetPeriod.HOURLY, datetime(2023, 1, 1, 1), datetime(2023, 1, 1), 2),
        (ResetPeriod.HOURLY, datetime(2023, 1, 1, 3), datetime(2023, 1, 1), 4),
        (ResetPeriod.WEEKLY, datetime(2023, 1, 1, 3), datetime(2023, 1, 1), 1),
        (ResetPeriod.WEEKLY, datetime(2023, 2, 1), datetime(2023, 1, 1), 5),
    ],
)
def test_reset_period_count_occurences_method(
    reset_period: ResetPeriod, until_datetime: datetime, ref_datetime: datetime, exp_num_occurences: int
) -> None:  # noqa
    """Given some input datetime, return the number of times since the reference time
    and until the 'until' time that the given ResetPeriod has occurred"""

    assert reset_period.count_occurences(until=until_datetime, reference=ref_datetime) == exp_num_occurences
