import random

import pytest
from whenever import ZonedDateTime

from pytariff.reset import ChargeMethod, ResetFrequency, ResetPeriod
from tests.synthetic_profiles import SYNTHETIC_PROFILE_B


class TestReset:
    @pytest.mark.parametrize(
        "subcls, expected_name, expected_value",
        [
            (ResetFrequency.DAILY, "DAILY", {"days": 1}),
            (ResetFrequency.WEEKLY, "WEEKLY", {"weeks": 1}),
            (ResetFrequency.MONTHLY, "MONTHLY", {"months": 1}),
            (ResetFrequency.QUARTERLY, "QUARTERLY", {"months": 3}),
        ],
    )
    def test_reset_frequency_enum(
        self, subcls: ResetFrequency, expected_name: str, expected_value: dict[str, int]
    ) -> None:
        """Assert that the ResetFrequency definition abides by expectations and that
        it is possible to map a string to its ResetFrequency if a subcls with
        that name in upper-case exists (or otherwise raise the appropriate Exception)"""

        assert getattr(subcls, "name") == expected_name
        assert getattr(subcls, "value") == expected_value

        # randomise case of expected_name so we can check veracity of _missing_ method
        rdm = "".join(random.choice((str.upper, str.lower))(x) for x in expected_name)
        wrong = expected_name[:-1]

        assert subcls == ResetFrequency(expected_name)
        assert subcls == ResetFrequency(rdm)

        with pytest.raises(ValueError):
            ResetFrequency(wrong)

    def test_charge_method(self) -> None:
        """TODO"""
        pass

    @pytest.mark.parametrize(
        "anchor, frequency, expected_next_reset",
        [
            (  # regular addition of single calendar day; no surprises
                ZonedDateTime(2024, 1, 1, tz="UTC"),
                ResetFrequency.DAILY,
                ZonedDateTime(2024, 1, 2, tz="UTC"),
            ),
            (  # regular addition of single calendar week; no surprises
                ZonedDateTime(2024, 1, 1, tz="UTC"),
                ResetFrequency.WEEKLY,
                ZonedDateTime(2024, 1, 8, tz="UTC"),
            ),
            (  # addition of calendar month; no date truncation
                ZonedDateTime(2024, 7, 31, tz="UTC"),
                ResetFrequency.MONTHLY,
                ZonedDateTime(2024, 8, 31, tz="UTC"),
            ),
            (  # addition of calendar month; date truncation
                ZonedDateTime(2024, 5, 31, tz="UTC"),
                ResetFrequency.MONTHLY,
                ZonedDateTime(2024, 6, 30, tz="UTC"),
            ),
            (  # addition of calendar month into ambiguous DST transition
                # taken from whenever docs
                ZonedDateTime(2023, 9, 29, 2, 15, tz="Europe/Amsterdam"),
                ResetFrequency.MONTHLY,
                ZonedDateTime(
                    2023,
                    10,
                    29,
                    2,
                    15,
                    tz="Europe/Amsterdam",
                    disambiguate="compatible",
                ),
            ),
            (  # addition of calendar day into ambiguous DST transition
                # note, we have added 23 (not 24) hours
                # taken from whenever docs
                ZonedDateTime(2023, 3, 25, 12, tz="Europe/Amsterdam"),
                ResetFrequency.DAILY,
                ZonedDateTime(2023, 3, 26, 12, tz="Europe/Amsterdam"),
            ),
        ],
    )
    def test_reset_period(
        self,
        anchor: ZonedDateTime,
        frequency: ResetFrequency,
        expected_next_reset: ZonedDateTime,
    ) -> None:
        """Assert that the ResetPeriod next_reset generator behaves as expected,
        particularly around DST transitions"""

        reset_period = ResetPeriod(anchor=anchor, frequency=frequency)
        assert next(reset_period.next_reset()) == expected_next_reset


def test_reset_period_get_transformed_profile() -> None:
    """TODO"""
    rp = ResetPeriod(
        anchor=ZonedDateTime(2024, 1, 1, tz="UTC"),
        frequency=ResetFrequency._MINUTELY,
        charge_method=ChargeMethod._Infinity,
    )

    transformed = rp.get_transformed_profile(
        SYNTHETIC_PROFILE_B, until=ZonedDateTime(2024, 1, 1, 0, 10, tz="UTC")
    )
