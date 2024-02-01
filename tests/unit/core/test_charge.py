from datetime import datetime
from zoneinfo import ZoneInfo
from pydantic import ValidationError
import pytest

from utal.core.block import ConsumptionBlock, DemandBlock, TariffBlock
from utal.core.charge import ConsumptionCharge, ExportConsumptionCharge, ImportConsumptionCharge, TariffCharge
from utal.core.typing import Consumption, Demand
from utal.core.unit import SignConvention, TradeDirection
from utal.core.reset import ResetData, ResetPeriod
from utal.core.rate import TariffRate, RateCurrency
from utal.core.unit import ConsumptionUnit, DemandUnit, TariffUnit


def test_tariff_charge_valid_construction():
    """Assert that it is possible to generate a valid instance of a TariffCharge, noting
    that it is not possible to instantiate the generic TariffUnit without a specific MetricType
    Unit or without a specific MetricType ResetPeriod"""

    TariffCharge(
        blocks=(
            TariffBlock(
                from_quantity=0,
                to_quantity=float("inf"),
                rate=TariffRate(currency=RateCurrency.AUD, value=1),
            ),
        ),
        unit=TariffUnit(metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive),
        reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
    ),


@pytest.mark.parametrize(
    "blocks_tuple, unit, reset_data, raises",
    [
        (
            (
                ConsumptionBlock(
                    rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    from_quantity=0,
                    to_quantity=100,
                ),
            ),
            ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive),
            ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            False,
        ),
        (
            (
                ConsumptionBlock(
                    rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    from_quantity=0,
                    to_quantity=100,
                ),
            ),
            ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive),
            ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            False,
        ),
        (
            (
                ConsumptionBlock(
                    rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    from_quantity=0,
                    to_quantity=100,
                ),
                ConsumptionBlock(
                    rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    from_quantity=100,
                    to_quantity=200,
                ),
            ),
            ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive),
            ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            False,
        ),
        (  # blocks with same parent charge cannot overlap (this would be an overlap in quantity + unit)
            (
                ConsumptionBlock(
                    rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    from_quantity=0,
                    to_quantity=100,
                ),
                ConsumptionBlock(
                    rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    from_quantity=100,
                    to_quantity=200,
                ),
            ),
            ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive),
            ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            False,
        ),
        (  # blocks with same parent charge cannot overlap (this would be an overlap in quantity + unit)
            (
                ConsumptionBlock(
                    rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    from_quantity=0,
                    to_quantity=100,
                ),
                ConsumptionBlock(
                    rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    from_quantity=50,
                    to_quantity=150,
                ),
            ),
            ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive),
            ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            True,
        ),
        (  # consumption charge cannot contain DemandUnit
            (
                ConsumptionBlock(
                    rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    from_quantity=0,
                    to_quantity=100,
                ),
            ),
            DemandUnit(metric=Demand.kW, direction=TradeDirection.Import, convention=SignConvention.Passive),
            ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            True,
        ),
        (  # consumption charge cannot contain DemandBlock
            (
                DemandBlock(
                    rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    from_quantity=0,
                    to_quantity=100,
                ),
            ),
            ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive),
            ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            True,
        ),
    ],
)
def test_consumption_charge_valid_construction(
    blocks_tuple: tuple[ConsumptionBlock, ...],
    unit: ConsumptionUnit | DemandUnit | None,
    reset_data: ResetData,
    raises: bool,
) -> None:
    """Assert that it is possible to instantiate a valid instance of a ConsumptionCharge using valid
    inputs, and otherwise that it is not possible. Specifically, child blocks cannot overlap in
    a single charge and must be ConsumptionBlocks, the unit must be an instance of a Consumption unit,
    and the reset data must be a ResetData"""
    if raises:
        with pytest.raises(ValidationError):
            ConsumptionCharge(blocks=blocks_tuple, unit=unit, reset_data=reset_data)
    else:
        assert ConsumptionCharge(blocks=blocks_tuple, unit=unit, reset_data=reset_data)


@pytest.mark.parametrize(
    "blocks_tuple",
    [
        (  # intersection
            (
                ConsumptionBlock(
                    unit=ConsumptionUnit(
                        metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                    ),
                    rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    from_quantity=0,
                    to_quantity=101,
                ),
                ConsumptionBlock(
                    unit=ConsumptionUnit(
                        metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                    ),
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
        ConsumptionCharge(
            blocks=blocks_tuple,
            unit=ConsumptionUnit(
                metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
            ),
            reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
        )


@pytest.mark.parametrize(
    "blocks_tuple, unit, reset_data, raises",
    [
        (
            (
                ConsumptionBlock(
                    rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    from_quantity=0,
                    to_quantity=100,
                ),
            ),
            ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive),
            ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            False,
        ),
        (
            (
                ConsumptionBlock(
                    rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    from_quantity=0,
                    to_quantity=100,
                ),
            ),
            ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Export, convention=SignConvention.Passive),
            ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            True,
        ),
    ],
)
def test_import_consumption_charge_must_import(
    blocks_tuple: tuple[ConsumptionBlock, ...],
    unit: ConsumptionUnit | DemandUnit | None,
    reset_data: ResetData,
    raises: bool,
) -> None:
    """"""
    if raises:
        with pytest.raises(ValidationError):
            ImportConsumptionCharge(
                blocks=blocks_tuple,
                unit=unit,
                reset_data=reset_data,
            )
    else:
        assert ImportConsumptionCharge(blocks=blocks_tuple, unit=unit, reset_data=reset_data)


@pytest.mark.parametrize(
    "blocks_tuple, unit, reset_data, raises",
    [
        (
            (
                ConsumptionBlock(
                    rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    from_quantity=0,
                    to_quantity=100,
                ),
            ),
            ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Export, convention=SignConvention.Passive),
            ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            False,
        ),
        (
            (
                ConsumptionBlock(
                    rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    from_quantity=0,
                    to_quantity=100,
                ),
            ),
            ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive),
            ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            True,
        ),
    ],
)
def test_export_consumption_charge_must_export(
    blocks_tuple: tuple[ConsumptionBlock, ...],
    unit: ConsumptionUnit | DemandUnit | None,
    reset_data: ResetData,
    raises: bool,
) -> None:
    """"""
    if raises:
        with pytest.raises(ValidationError):
            ExportConsumptionCharge(
                blocks=blocks_tuple,
                unit=unit,
                reset_data=reset_data,
            )
    else:
        assert ExportConsumptionCharge(blocks=blocks_tuple, unit=unit, reset_data=reset_data)


@pytest.mark.parametrize(
    "charge_a, charge_b, expected_intersection",
    [
        (  # charge_a subsumes charge_b
            ConsumptionCharge(  # charge_a
                blocks=(
                    ConsumptionBlock(
                        rate=TariffRate(currency=RateCurrency.AUD, value=1), from_quantity=0, to_quantity=float("inf")
                    ),
                ),
                unit=ConsumptionUnit(
                    metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                ),
                reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            ),
            ConsumptionCharge(  # charge_b
                blocks=(
                    ConsumptionBlock(
                        rate=TariffRate(currency=RateCurrency.AUD, value=1), from_quantity=50, to_quantity=100
                    ),
                ),
                unit=ConsumptionUnit(
                    metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                ),
                reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            ),
            ConsumptionCharge(  # expected
                blocks=(ConsumptionBlock(rate=None, from_quantity=50, to_quantity=100),),
                unit=ConsumptionUnit(
                    metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                ),
                reset_data=None,
            ),
        ),
        (  # charge_a right-overhangs charge_b
            ConsumptionCharge(  # charge_a
                blocks=(
                    ConsumptionBlock(
                        rate=TariffRate(currency=RateCurrency.AUD, value=1), from_quantity=0, to_quantity=100
                    ),
                ),
                unit=ConsumptionUnit(
                    metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                ),
                reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            ),
            ConsumptionCharge(  # charge_b
                blocks=(
                    ConsumptionBlock(
                        rate=TariffRate(currency=RateCurrency.AUD, value=1), from_quantity=50, to_quantity=100
                    ),
                ),
                unit=ConsumptionUnit(
                    metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                ),
                reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            ),
            ConsumptionCharge(  # expected
                blocks=(ConsumptionBlock(rate=None, from_quantity=50, to_quantity=100),),
                unit=ConsumptionUnit(
                    metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                ),
                reset_data=None,
            ),
        ),
        (  # charge_a left-overhangs charge_b
            ConsumptionCharge(  # charge_a
                blocks=(
                    ConsumptionBlock(
                        rate=TariffRate(currency=RateCurrency.AUD, value=1), from_quantity=50, to_quantity=100
                    ),
                ),
                unit=ConsumptionUnit(
                    metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                ),
                reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            ),
            ConsumptionCharge(  # charge_b
                blocks=(
                    ConsumptionBlock(
                        rate=TariffRate(currency=RateCurrency.AUD, value=1), from_quantity=0, to_quantity=100
                    ),
                ),
                unit=ConsumptionUnit(
                    metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                ),
                reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            ),
            ConsumptionCharge(  # expected
                blocks=(ConsumptionBlock(rate=None, from_quantity=50, to_quantity=100),),
                unit=ConsumptionUnit(
                    metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                ),
                reset_data=None,
            ),
        ),
        (  # no overlaps from quantity
            ConsumptionCharge(  # charge_a
                blocks=(
                    ConsumptionBlock(
                        rate=TariffRate(currency=RateCurrency.AUD, value=1), from_quantity=50, to_quantity=100
                    ),
                ),
                unit=ConsumptionUnit(
                    metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                ),
                reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            ),
            ConsumptionCharge(  # charge_b
                blocks=(
                    ConsumptionBlock(
                        rate=TariffRate(currency=RateCurrency.AUD, value=1), from_quantity=100, to_quantity=200
                    ),
                ),
                unit=ConsumptionUnit(
                    metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                ),
                reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            ),
            None,
        ),
        (  # no overlaps due to unit misalignment
            ConsumptionCharge(  # charge_a
                blocks=(
                    ConsumptionBlock(
                        rate=TariffRate(currency=RateCurrency.AUD, value=1), from_quantity=50, to_quantity=100
                    ),
                ),
                unit=ConsumptionUnit(
                    metric=Consumption._null, direction=TradeDirection.Import, convention=SignConvention.Passive
                ),
                reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            ),
            ConsumptionCharge(  # charge_b
                blocks=(
                    ConsumptionBlock(
                        rate=TariffRate(currency=RateCurrency.AUD, value=1), from_quantity=100, to_quantity=200
                    ),
                ),
                unit=ConsumptionUnit(
                    metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                ),
                reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            ),
            None,
        ),
        (  # multiple blocks per charge; more complex
            ConsumptionCharge(  # charge_a
                blocks=(
                    ConsumptionBlock(
                        rate=TariffRate(currency=RateCurrency.AUD, value=1), from_quantity=0, to_quantity=50
                    ),
                    ConsumptionBlock(
                        rate=TariffRate(currency=RateCurrency.AUD, value=1), from_quantity=50, to_quantity=100
                    ),
                ),
                unit=ConsumptionUnit(
                    metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                ),
                reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            ),
            ConsumptionCharge(  # charge_b
                blocks=(
                    ConsumptionBlock(
                        rate=TariffRate(currency=RateCurrency.AUD, value=1), from_quantity=25, to_quantity=75
                    ),
                    ConsumptionBlock(
                        rate=TariffRate(currency=RateCurrency.AUD, value=1), from_quantity=75, to_quantity=125
                    ),
                ),
                unit=ConsumptionUnit(
                    metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                ),
                reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            ),
            ConsumptionCharge(  # expected: overlap from a[0]&b[0], a[1]&b[0], and a[1]&b[1]
                blocks=(
                    ConsumptionBlock(rate=None, from_quantity=25, to_quantity=50),
                    ConsumptionBlock(rate=None, from_quantity=50, to_quantity=75),
                    ConsumptionBlock(rate=None, from_quantity=75, to_quantity=100),
                ),
                unit=ConsumptionUnit(
                    metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                ),
                reset_data=None,
            ),
        ),
    ],
)
def test_consumption_charge_intersection_method(
    charge_a: ConsumptionCharge,
    charge_b: ConsumptionCharge | TariffCharge,
    expected_intersection: ConsumptionCharge | None,
) -> None:
    intersection = charge_a & charge_b
    assert intersection == expected_intersection


@pytest.mark.parametrize(
    "charge_a, charge_b, is_equal",
    [
        (
            TariffCharge(
                blocks=(
                    TariffBlock(
                        from_quantity=0,
                        to_quantity=float("inf"),
                        rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    ),
                ),
                unit=TariffUnit(
                    metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                ),
                reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            ),
            TariffCharge(
                blocks=(
                    TariffBlock(
                        from_quantity=0,
                        to_quantity=float("inf"),
                        rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    ),
                ),
                unit=TariffUnit(
                    metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                ),
                reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            ),
            True,
        ),
        (  # different child blocks
            TariffCharge(
                blocks=(
                    TariffBlock(
                        from_quantity=0,
                        to_quantity=float("inf"),
                        rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    ),
                ),
                unit=TariffUnit(
                    metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                ),
                reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            ),
            TariffCharge(
                blocks=(
                    TariffBlock(
                        from_quantity=0,
                        to_quantity=float("inf"),
                        rate=TariffRate(currency=RateCurrency.AUD, value=2),
                    ),
                ),
                unit=TariffUnit(
                    metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                ),
                reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            ),
            False,
        ),
        (  # different unit directions
            TariffCharge(
                blocks=(
                    TariffBlock(
                        from_quantity=0,
                        to_quantity=float("inf"),
                        rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    ),
                ),
                unit=TariffUnit(
                    metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                ),
                reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            ),
            TariffCharge(
                blocks=(
                    TariffBlock(
                        from_quantity=0,
                        to_quantity=float("inf"),
                        rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    ),
                ),
                unit=TariffUnit(
                    metric=Consumption.kWh, direction=TradeDirection.Export, convention=SignConvention.Passive
                ),
                reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            ),
            False,
        ),
        (  # different reset_data
            TariffCharge(
                blocks=(
                    TariffBlock(
                        from_quantity=0,
                        to_quantity=float("inf"),
                        rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    ),
                ),
                unit=TariffUnit(
                    metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                ),
                reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            ),
            TariffCharge(
                blocks=(
                    TariffBlock(
                        from_quantity=0,
                        to_quantity=float("inf"),
                        rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    ),
                ),
                unit=TariffUnit(
                    metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                ),
                reset_data=ResetData(
                    anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.HALF_HOURLY
                ),
            ),
            False,
        ),
    ],
)
def test_tariff_charge_hash(charge_a: TariffCharge, charge_b: TariffCharge, is_equal: bool) -> None:
    assert (charge_a == charge_b) is is_equal
    if is_equal:
        assert hash(charge_a) == hash(charge_b)
    else:
        assert hash(charge_a) != hash(charge_b)
