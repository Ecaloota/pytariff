import pytest

from utal.schema.block import ConsumptionBlock
from utal.schema.generic_types import Import
from utal.schema.rate import TariffRate
from utal.schema.unit import ConsumptionUnit, RateCurrency


@pytest.fixture
def DEFAULT_BLOCK():
    return ConsumptionBlock(
        block_type=Import,
        from_quantity=0,
        to_quantity=float("inf"),
        unit=ConsumptionUnit.kWh,
        rate=TariffRate(currency=RateCurrency.AUD, value=1),
    )
