import pytest

from utal.schema.block import ConsumptionBlock
from utal.schema.charge import ConsumptionCharge
from utal.schema.rate import TariffRate
from utal.schema.unit import ConsumptionUnit, RateCurrency


@pytest.mark.parametrize(
    "blocks_tuple",
    [
        (
            (
                ConsumptionBlock(
                    unit=ConsumptionUnit.kWh,
                    rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    from_quantity=0,
                    to_quantity=100,
                ),
            )
        ),
        (
            (
                ConsumptionBlock(
                    unit=ConsumptionUnit.kWh,
                    rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    from_quantity=0,
                    to_quantity=100,
                ),
                ConsumptionBlock(
                    unit=ConsumptionUnit.kWh,
                    rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    from_quantity=100,
                    to_quantity=200,
                ),
            )
        ),
    ],
)
def test_consumption_charge_valid_construction(blocks_tuple: tuple[ConsumptionBlock, ...]) -> None:
    """"""
    ConsumptionCharge(blocks=blocks_tuple)


@pytest.mark.parametrize(
    "blocks_tuple",
    [
        (  # intersection
            (
                ConsumptionBlock(
                    unit=ConsumptionUnit.kWh,
                    rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    from_quantity=0,
                    to_quantity=101,
                ),
                ConsumptionBlock(
                    unit=ConsumptionUnit.kWh,
                    rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    from_quantity=100,
                    to_quantity=200,
                ),
            )
        ),
    ],
)
def test_consumption_charge_cannot_intersect(blocks_tuple: tuple[ConsumptionBlock, ...]) -> None:
    """"""
    with pytest.raises(ValueError):
        ConsumptionCharge(blocks=blocks_tuple)
