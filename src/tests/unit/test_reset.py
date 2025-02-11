import random

import pytest

from pytariff.reset import ResetFrequency


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

    # TODO test the next_reset generator specifically over normal and unintuitive DST
    # transitions. Assert that the way we are calling the current.add(**self.frequency.value)
    # is robust w.r.t. each of the ResetFrequency values.
    def test_reset_period(self) -> None:
        """TODO"""
        pass
