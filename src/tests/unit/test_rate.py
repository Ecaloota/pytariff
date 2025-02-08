from typing import Any, Callable

import pytest

from pytariff.rate import TariffRate


class TestTariffRate:
    def test_tariff_rate_get_value_cases(
        self,
        value: float | Callable[..., float],
        vargs: tuple[Any, ...],
        expected_return: float,
    ) -> None:
        """Given a valid value for the value attribute of a
        TariffRate, assert that attempting to access the .value
        attribute directly raises an AttributeError, and that
        calling the get_value method with the provided args
        returns the expected value."""

        rate = TariffRate(currency="AUD", value=value)

        with pytest.raises(AttributeError):
            rate.value

        assert rate.get_value(*vargs) == expected_return
