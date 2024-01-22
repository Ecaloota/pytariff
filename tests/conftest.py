import pytest

from utal._internal.block import ConsumptionBlock, DemandBlock
from utal._internal.generic_types import Consumption, Demand, SignConvention, TradeDirection
from utal._internal.rate import TariffRate
from utal._internal.unit import ConsumptionUnit, DemandUnit, RateCurrency


@pytest.fixture
def DEFAULT_CONSUMPTION_BLOCK():
    return ConsumptionBlock(
        from_quantity=0,
        to_quantity=float("inf"),
        unit=ConsumptionUnit(
            metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
        ),
        rate=TariffRate(currency=RateCurrency.AUD, value=1),
    )


@pytest.fixture
def DEFAULT_DEMAND_BLOCK():
    return DemandBlock(
        from_quantity=0,
        to_quantity=float("inf"),
        unit=DemandUnit(metric=Demand.kW, direction=TradeDirection.Import, convention=SignConvention.Passive),
        rate=TariffRate(currency=RateCurrency.AUD, value=1),
    )
