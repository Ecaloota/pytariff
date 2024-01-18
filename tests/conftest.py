import pytest

from utal.schema.block import ConsumptionBlock
from utal.schema.generic_types import Consumption, TradeDirection
from utal.schema.rate import TariffRate
from utal.schema.unit import ConsumptionUnit, RateCurrency


@pytest.fixture
def DEFAULT_BLOCK():
    return ConsumptionBlock(
        block_type=TradeDirection.Import,
        from_quantity=0,
        to_quantity=float("inf"),
        unit=ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
        rate=TariffRate(currency=RateCurrency.AUD, value=1),
    )
