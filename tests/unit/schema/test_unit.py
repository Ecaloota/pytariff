from typing import Any
from pydantic import ValidationError
import pytest
from utal.schema.generic_types import Consumption, Demand, TradeDirection

from utal.schema.unit import ConsumptionUnit, DemandUnit


@pytest.mark.parametrize(
    "metric, direction, raises",
    [
        (Consumption.kWh, TradeDirection.Import, False),
        (Consumption.kWh, TradeDirection.Export, False),
        (Consumption._null, TradeDirection.Import, False),
        (Consumption._null, TradeDirection.Export, False),
        (Demand._null, TradeDirection.Export, True),
        (Demand.kW, TradeDirection.Export, True),
    ],
)
def test_consumption_unit(metric: Any, direction: TradeDirection, raises: bool) -> None:
    if raises:
        with pytest.raises(ValidationError):
            ConsumptionUnit(metric=metric, direction=direction)
    else:
        assert ConsumptionUnit(metric=metric, direction=direction)


@pytest.mark.parametrize(
    "metric, direction, raises",
    [
        (Demand.kW, TradeDirection.Import, False),
        (Demand.kW, TradeDirection.Export, False),
        (Demand._null, TradeDirection.Import, False),
        (Demand._null, TradeDirection.Export, False),
        (Consumption._null, TradeDirection.Export, True),
        (Consumption.kWh, TradeDirection.Export, True),
    ],
)
def test_demand_unit(metric: Any, direction: TradeDirection, raises: bool) -> None:
    if raises:
        with pytest.raises(ValidationError):
            DemandUnit(metric=metric, direction=direction)
    else:
        assert DemandUnit(metric=metric, direction=direction)
