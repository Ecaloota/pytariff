import pytest

from pytariff.core.block import ConsumptionBlock, DemandBlock
from pytariff.core.typing import Consumption, Demand
from pytariff.core.rate import TariffRate
from pytariff.core.unit import ConsumptionUnit, DemandUnit, SignConvention, TradeDirection


@pytest.fixture
def DEFAULT_CONSUMPTION_BLOCK():
    return ConsumptionBlock(
        from_quantity=0,
        to_quantity=float("inf"),
        unit=ConsumptionUnit(
            metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
        ),
        rate=TariffRate(currency="AUD", value=1),
    )


@pytest.fixture
def DEFAULT_DEMAND_BLOCK():
    return DemandBlock(
        from_quantity=0,
        to_quantity=float("inf"),
        unit=DemandUnit(metric=Demand.kW, direction=TradeDirection.Import, convention=SignConvention.Passive),
        rate=TariffRate(currency="AUD", value=1),
    )
