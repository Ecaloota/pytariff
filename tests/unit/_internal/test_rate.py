from typing import Any

import pytest
from pydantic import ValidationError

from utal._internal.rate import TariffRate
from utal._internal.currency import RateCurrency


@pytest.mark.parametrize(
    "currency, value",
    [
        (RateCurrency.AUD, float("inf")),
        (RateCurrency.AUD, 0),
        (RateCurrency.AUD, float("-inf")),
        (RateCurrency.AUD, 10),
        (RateCurrency.AUD, "5"),
    ],
)
def test_tariff_rate_valid_construction(currency: RateCurrency, value: float):
    TariffRate(currency=currency, value=value)


@pytest.mark.parametrize(
    "currency, value",
    [
        ("DNE", float("-inf")),
        (RateCurrency.AUD, "DNE"),
    ],
)
def test_tariff_rate_invalid_construction(currency: Any, value: Any):
    with pytest.raises(ValidationError):
        TariffRate(currency=currency, value=value)
