from typing import Any, Optional

import pytest
from pydantic import ValidationError

from utal.schema.block import ConsumptionBlock
from utal.schema.rate import TariffRate
from utal.schema.unit import ConsumptionUnit, DemandUnit, RateCurrency


@pytest.mark.parametrize(
    "from_quantity, to_quantity, unit, rate",
    [
        (0, float("inf"), ConsumptionUnit.kWh, TariffRate(currency=RateCurrency.AUD, value=1)),
    ],
)
def test_consumption_block_valid_construction(
    from_quantity: float, to_quantity: float, unit: ConsumptionUnit, rate: TariffRate
) -> None:
    """TODO"""

    ConsumptionBlock(
        from_quantity=from_quantity,
        to_quantity=to_quantity,
        unit=unit,
        rate=rate,
    )


@pytest.mark.parametrize(
    "from_quantity, to_quantity, unit, rate",
    [
        (0, float("inf"), DemandUnit.kW, TariffRate(currency=RateCurrency.AUD, value=1)),
        (0, float("inf"), DemandUnit.kW, TariffRate(currency=RateCurrency.AUD, value=1)),
        (100, 100, DemandUnit.kW, TariffRate(currency=RateCurrency.AUD, value=1)),
        (1000, 50, DemandUnit.kW, TariffRate(currency=RateCurrency.AUD, value=1)),
    ],
)
def test_consumption_block_invalid_construction(from_quantity: Any, to_quantity: Any, unit: Any, rate: Any) -> None:
    """TODO"""

    with pytest.raises(ValidationError):
        ConsumptionBlock(
            from_quantity=from_quantity,
            to_quantity=to_quantity,
            unit=unit,
            rate=rate,
        )


@pytest.mark.parametrize(
    "block_1, block_2, expected_intersection",
    [
        (
            ConsumptionBlock(
                from_quantity=0,
                to_quantity=float("inf"),
                unit=ConsumptionUnit.kWh,
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=50,
                to_quantity=100,
                unit=ConsumptionUnit.kWh,
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=50,
                to_quantity=100,
                unit=ConsumptionUnit.kWh,
                rate=None,
            ),
        ),
        (
            ConsumptionBlock(
                from_quantity=25,
                to_quantity=75,
                unit=ConsumptionUnit.kWh,
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=50,
                to_quantity=100,
                unit=ConsumptionUnit.kWh,
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=50,
                to_quantity=75,
                unit=ConsumptionUnit.kWh,
                rate=None,
            ),
        ),
        (
            ConsumptionBlock(
                from_quantity=50,
                to_quantity=100,
                unit=ConsumptionUnit.kWh,
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=50,
                to_quantity=100,
                unit=ConsumptionUnit.kWh,
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=50,
                to_quantity=100,
                unit=ConsumptionUnit.kWh,
                rate=None,
            ),
        ),
        (
            ConsumptionBlock(
                from_quantity=50,
                to_quantity=100,
                unit=ConsumptionUnit.kWh,
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=50,
                to_quantity=100,
                unit=ConsumptionUnit._null,
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            None,
        ),
        (
            ConsumptionBlock(
                from_quantity=0,
                to_quantity=100,
                unit=ConsumptionUnit.kWh,
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=100,
                to_quantity=200,
                unit=ConsumptionUnit._null,
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            None,
        ),
    ],
)
def test_consumption_block_intersection(
    block_1: ConsumptionBlock, block_2: ConsumptionBlock, expected_intersection: Optional[ConsumptionBlock]
) -> None:
    """TODO"""

    if expected_intersection is None:
        assert (block_1 & block_2) is expected_intersection
    else:
        assert (block_1 & block_2).quantities_and_types_equal(expected_intersection)


@pytest.mark.parametrize(
    "block_1, obj",
    [
        (
            ConsumptionBlock(
                from_quantity=0,
                to_quantity=float("inf"),
                unit=ConsumptionUnit.kWh,
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            int(5),
        ),
    ],
)
def test_consumption_block_invalid_intersection(block_1: ConsumptionBlock, obj: Any) -> None:
    """TODO"""

    with pytest.raises(ValueError):
        block_1 & obj
