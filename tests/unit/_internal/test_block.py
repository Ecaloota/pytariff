from typing import Any, Optional

import pytest
from pydantic import ValidationError

from utal._internal.block import ConsumptionBlock, TariffBlock
from utal._internal.generic_types import Consumption
from utal._internal.rate import TariffRate
from utal._internal.unit import RateCurrency


@pytest.mark.parametrize(
    "from_quantity, to_quantity, rate, raises",
    [
        (  # valid ConsumptionBlock attribute values
            0,
            float("inf"),
            TariffRate(currency=RateCurrency.AUD, value=1),
            False,
        ),
        (  # from_quantity <= to_quantity
            100,
            100,
            TariffRate(currency=RateCurrency.AUD, value=1),
            True,
        ),
        (  # from_quantity <= to_quantity
            1000,
            50,
            TariffRate(currency=RateCurrency.AUD, value=1),
            True,
        ),
    ],
)
def test_consumption_block_construction(
    from_quantity: float, to_quantity: float, rate: TariffRate, raises: bool
) -> None:
    """Assert that it is possible to generate an instance of a ConsumptionBlock
    using the provided attributes if !raises, else that trying to generate an instance
    with the provided attributes raises a ValidationError"""

    if raises:
        with pytest.raises(ValidationError):
            ConsumptionBlock(
                from_quantity=from_quantity,
                to_quantity=to_quantity,
                rate=rate,
            )
    else:
        ConsumptionBlock(
            from_quantity=from_quantity,
            to_quantity=to_quantity,
            rate=rate,
        )


@pytest.mark.parametrize(
    "block_1, block_2, expected_intersection",
    [
        (  # block_2 contained within block_1
            ConsumptionBlock(
                from_quantity=0,
                to_quantity=float("inf"),
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=50,
                to_quantity=100,
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=50,
                to_quantity=100,
                rate=None,
            ),
        ),
        (
            ConsumptionBlock(
                from_quantity=25,
                to_quantity=75,
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=50,
                to_quantity=100,
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=50,
                to_quantity=75,
                rate=None,
            ),
        ),
        (  # overlap between two identical ConsumptionBlocks is that Block minus the rate
            ConsumptionBlock(
                from_quantity=50,
                to_quantity=100,
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=50,
                to_quantity=100,
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=50,
                to_quantity=100,
                rate=None,
            ),
        ),
        (
            ConsumptionBlock(
                from_quantity=0,
                to_quantity=100,
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=100,
                to_quantity=200,
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
        assert (block_1 & block_2) == expected_intersection


@pytest.mark.parametrize(
    "block_1, obj",
    [
        (
            ConsumptionBlock(
                from_quantity=0,
                to_quantity=float("inf"),
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


@pytest.mark.parametrize(
    "block1, block2, is_equal",
    [
        (
            ConsumptionBlock(
                from_quantity=0,
                to_quantity=float("inf"),
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=0,
                to_quantity=float("inf"),
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            True,
        ),
        (  # from_quantity differs
            ConsumptionBlock(
                from_quantity=1,
                to_quantity=float("inf"),
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=0,
                to_quantity=float("inf"),
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            False,
        ),
        (  # to_quantity differs
            ConsumptionBlock(
                from_quantity=0,
                to_quantity=1,
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=0,
                to_quantity=float("inf"),
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            False,
        ),
        (  # rate changes in value
            ConsumptionBlock(
                from_quantity=0,
                to_quantity=float("inf"),
                rate=TariffRate(RateCurrency.AUD, value=2),
            ),
            ConsumptionBlock(
                from_quantity=0,
                to_quantity=float("inf"),
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            False,
        ),
    ],
)
def test_consumption_block_equality(block1: ConsumptionBlock, block2: ConsumptionBlock, is_equal: bool) -> None:
    assert (block1 == block2) is is_equal


@pytest.mark.parametrize(
    "block_a, block_b, is_equal",
    [
        (
            TariffBlock(
                rate=TariffRate(currency=RateCurrency.AUD, value=1.0), from_quantity=0.0, to_quantity=float("inf")
            ),
            TariffBlock(
                rate=TariffRate(currency=RateCurrency.AUD, value=1.0), from_quantity=0.0, to_quantity=float("inf")
            ),
            True,
        ),
        (
            TariffBlock(
                rate=TariffRate(currency=RateCurrency.AUD, value=2.0), from_quantity=0.0, to_quantity=float("inf")
            ),
            TariffBlock(
                rate=TariffRate(currency=RateCurrency.AUD, value=1.0), from_quantity=0.0, to_quantity=float("inf")
            ),
            False,
        ),
    ],
)
def test_tariff_block_hash(block_a: TariffBlock, block_b: TariffBlock, is_equal: bool) -> None:
    if is_equal:
        assert (block_a == block_b) is is_equal
        assert hash(block_a) == hash(block_b)
    else:
        assert (block_a == block_b) is is_equal
        assert hash(block_a) != hash(block_b)
