from typing import Any, Optional

import pytest
from pydantic import ValidationError

from utal.schema.block import ConsumptionBlock, ExportConsumptionBlock, ImportConsumptionBlock
from utal.schema.generic_types import Consumption, Demand, TradeDirection
from utal.schema.rate import TariffRate
from utal.schema.unit import ConsumptionUnit, DemandUnit, RateCurrency
from utal.schema.generic_types import MetricType


@pytest.mark.parametrize(
    "from_quantity, to_quantity, unit, rate, raises",
    [
        (
            0,
            float("inf"),
            ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
            TariffRate(currency=RateCurrency.AUD, value=1),
            False,
        ),
        (
            0,
            float("inf"),
            DemandUnit(metric=Demand.kW, direction=TradeDirection.Import),
            TariffRate(currency=RateCurrency.AUD, value=1),
            True,
        ),
        (
            0,
            float("inf"),
            DemandUnit(metric=Demand.kW, direction=TradeDirection.Import),
            TariffRate(currency=RateCurrency.AUD, value=1),
            True,
        ),
        (
            100,
            100,
            DemandUnit(metric=Demand.kW, direction=TradeDirection.Import),
            TariffRate(currency=RateCurrency.AUD, value=1),
            True,
        ),
        (
            1000,
            50,
            DemandUnit(metric=Demand.kW, direction=TradeDirection.Import),
            TariffRate(currency=RateCurrency.AUD, value=1),
            True,
        ),
    ],
)
def test_consumption_block_construction(
    from_quantity: float, to_quantity: float, unit: MetricType, rate: TariffRate, raises: bool
) -> None:
    """TODO"""

    if raises:
        with pytest.raises(ValidationError):
            ConsumptionBlock(
                from_quantity=from_quantity,
                to_quantity=to_quantity,
                unit=unit,
                rate=rate,
            )
    else:
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
                unit=ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=50,
                to_quantity=100,
                unit=ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=50,
                to_quantity=100,
                unit=ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
                rate=None,
            ),
        ),
        (
            ConsumptionBlock(
                from_quantity=25,
                to_quantity=75,
                unit=ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=50,
                to_quantity=100,
                unit=ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=50,
                to_quantity=75,
                unit=ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
                rate=None,
            ),
        ),
        (
            ConsumptionBlock(
                from_quantity=50,
                to_quantity=100,
                unit=ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=50,
                to_quantity=100,
                unit=ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=50,
                to_quantity=100,
                unit=ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
                rate=None,
            ),
        ),
        (
            ConsumptionBlock(
                from_quantity=50,
                to_quantity=100,
                unit=ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=50,
                to_quantity=100,
                unit=ConsumptionUnit(metric=Consumption._null, direction=TradeDirection.Import),
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            None,
        ),
        (
            ConsumptionBlock(
                from_quantity=0,
                to_quantity=100,
                unit=ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=100,
                to_quantity=200,
                unit=ConsumptionUnit(metric=Consumption._null, direction=TradeDirection.Import),
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
                unit=ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
                rate=TariffRate[Consumption](RateCurrency.AUD, value=1),
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
                unit=ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=0,
                to_quantity=float("inf"),
                unit=ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            True,
        ),
        (  # from_quantity differs
            ConsumptionBlock(
                from_quantity=1,
                to_quantity=float("inf"),
                unit=ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=0,
                to_quantity=float("inf"),
                unit=ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            False,
        ),
        (  # to_quantity differs
            ConsumptionBlock(
                from_quantity=0,
                to_quantity=1,
                unit=ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=0,
                to_quantity=float("inf"),
                unit=ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            False,
        ),
        (  # unit differs in direction
            ConsumptionBlock(
                from_quantity=0,
                to_quantity=float("inf"),
                unit=ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            ConsumptionBlock(
                from_quantity=0,
                to_quantity=float("inf"),
                unit=ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Export),
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            False,
        ),
        (  # rate changes in value
            ConsumptionBlock(
                from_quantity=0,
                to_quantity=float("inf"),
                unit=ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
                rate=TariffRate(RateCurrency.AUD, value=2),
            ),
            ConsumptionBlock(
                from_quantity=0,
                to_quantity=float("inf"),
                unit=ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
                rate=TariffRate(RateCurrency.AUD, value=1),
            ),
            False,
        ),
    ],
)
def test_consumption_block_equality(block1: ConsumptionBlock, block2: ConsumptionBlock, is_equal: bool) -> None:
    assert (block1 == block2) is is_equal


@pytest.mark.parametrize(
    "unit, raises",
    [
        (ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import), False),
        (ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Export), True),
    ],
)
def test_import_consumption_block_enforces_trade_import(unit: ConsumptionUnit, raises: bool) -> None:
    if raises:
        with pytest.raises(ValidationError):
            ImportConsumptionBlock(unit=unit, rate=None, from_quantity=0, to_quantity=1)
    else:
        assert ImportConsumptionBlock(unit=unit, rate=None, from_quantity=0, to_quantity=1)


@pytest.mark.parametrize(
    "unit, raises",
    [
        (ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import), True),
        (ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Export), False),
    ],
)
def test_export_consumption_block_enforces_trade_export(unit: ConsumptionUnit, raises: bool) -> None:
    if raises:
        with pytest.raises(ValidationError):
            ExportConsumptionBlock(unit=unit, rate=None, from_quantity=0, to_quantity=1)
    else:
        assert ExportConsumptionBlock(unit=unit, rate=None, from_quantity=0, to_quantity=1)
