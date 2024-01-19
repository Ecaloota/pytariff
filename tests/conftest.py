import pytest

from utal.schema.block import ConsumptionBlock, DemandBlock
from utal.schema.generic_types import Consumption, Demand, TradeDirection
from utal.schema.rate import TariffRate
from utal.schema.unit import ConsumptionUnit, DemandUnit, RateCurrency


@pytest.fixture
def DEFAULT_CONSUMPTION_BLOCK():
    return ConsumptionBlock(
        from_quantity=0,
        to_quantity=float("inf"),
        unit=ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
        rate=TariffRate(currency=RateCurrency.AUD, value=1),
    )


@pytest.fixture
def DEFAULT_DEMAND_BLOCK():
    return DemandBlock(
        from_quantity=0,
        to_quantity=float("inf"),
        unit=DemandUnit(metric=Demand.kW, direction=TradeDirection.Import),
        rate=TariffRate(currency=RateCurrency.AUD, value=1),
    )
