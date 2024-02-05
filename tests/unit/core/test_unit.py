from typing import Any
from pydantic import ValidationError
import pytest
from pytariff.core.typing import Consumption, Demand
from pytariff.core.unit import SignConvention, TradeDirection

from pytariff.core.unit import ConsumptionUnit, DemandUnit


@pytest.mark.parametrize(
    "metric, direction, convention, raises",
    [
        (Consumption.kWh, TradeDirection.Import, SignConvention.Passive, False),
        (Consumption.kWh, TradeDirection.Export, SignConvention.Passive, False),
        (Consumption._null, TradeDirection.Import, SignConvention.Passive, False),
        (Consumption._null, TradeDirection.Export, SignConvention.Passive, False),
        (Demand._null, TradeDirection.Export, SignConvention.Passive, True),
        (Demand.kW, TradeDirection.Export, SignConvention.Passive, True),
    ],
)
def test_consumption_unit(metric: Any, direction: TradeDirection, convention: SignConvention, raises: bool) -> None:
    if raises:
        with pytest.raises(ValidationError):
            ConsumptionUnit(metric=metric, direction=direction, convention=convention)
    else:
        assert ConsumptionUnit(metric=metric, direction=direction, convention=convention)


@pytest.mark.parametrize(
    "metric, direction, convention, raises",
    [
        (Demand.kW, TradeDirection.Import, SignConvention.Passive, False),
        (Demand.kW, TradeDirection.Export, SignConvention.Passive, False),
        (Demand._null, TradeDirection.Import, SignConvention.Passive, False),
        (Demand._null, TradeDirection.Export, SignConvention.Passive, False),
        (Consumption._null, TradeDirection.Export, SignConvention.Passive, True),
        (Consumption.kWh, TradeDirection.Export, SignConvention.Passive, True),
    ],
)
def test_demand_unit(metric: Any, direction: TradeDirection, convention: SignConvention, raises: bool) -> None:
    if raises:
        with pytest.raises(ValidationError):
            DemandUnit(metric=metric, direction=direction, convention=convention)
    else:
        assert DemandUnit(metric=metric, direction=direction, convention=convention)
