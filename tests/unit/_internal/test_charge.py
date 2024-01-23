from pydantic import ValidationError
import pytest

from utal._internal.block import ConsumptionBlock, DemandBlock, TariffBlock
from utal._internal.charge import ConsumptionCharge, ExportConsumptionCharge, ImportConsumptionCharge, TariffCharge
from utal._internal.generic_types import Consumption, Demand, SignConvention, TradeDirection
from utal._internal.period import ConsumptionResetPeriod, DemandResetPeriod, ResetPeriod
from utal._internal.rate import TariffRate
from utal._internal.unit import ConsumptionUnit, DemandUnit, RateCurrency, TariffUnit


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
        reset_period=ConsumptionResetPeriod.ANNUALLY,
    ),


@pytest.mark.parametrize(
    "blocks_tuple, unit, reset_period, raises",
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
            None,
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
            ConsumptionResetPeriod.DAILY,
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
            None,
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
            None,
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
            None,
            True,
        ),
        (
            (  # parameterized generics can't be used in the isinstance validation check
                TariffBlock[Consumption](
                    rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    from_quantity=0,
                    to_quantity=100,
                ),
            ),
            ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive),
            None,
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
            None,
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
            None,
            True,
        ),
        (  # ConsumptionCharge cannot contain DemandResetPeriod
            (
                ConsumptionBlock(
                    rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    from_quantity=0,
                    to_quantity=100,
                ),
            ),
            ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive),
            DemandResetPeriod.DAILY,
            True,
        ),
    ],
)
def test_consumption_charge_valid_construction(
    blocks_tuple: tuple[ConsumptionBlock, ...],
    unit: ConsumptionUnit | DemandUnit | None,
    reset_period: ResetPeriod,
    raises: bool,
) -> None:
    """Assert that it is possible to instantiate a valid instance of a ConsumptionCharge using valid
    inputs, and otherwise that it is not possible. Specifically, child blocks cannot overlap in
    a single charge and must be ConsumptionBlocks, the unit must be an instance of a Consumption unit,
    and the reset period must be a ConsumptionResetPeriod"""
    if raises:
        with pytest.raises(ValidationError):
            ConsumptionCharge(
                blocks=blocks_tuple,
                unit=unit,
                reset_period=reset_period,
            )
    else:
        assert ConsumptionCharge(blocks=blocks_tuple, unit=unit, reset_period=reset_period)


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
        ConsumptionCharge(blocks=blocks_tuple)


@pytest.mark.parametrize(
    "blocks_tuple, unit, reset_period, raises",
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
            None,
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
            None,
            True,
        ),
    ],
)
def test_import_consumption_charge_must_import(
    blocks_tuple: tuple[ConsumptionBlock, ...],
    unit: ConsumptionUnit | DemandUnit | None,
    reset_period: ResetPeriod,
    raises: bool,
) -> None:
    """"""
    if raises:
        with pytest.raises(ValidationError):
            ImportConsumptionCharge(
                blocks=blocks_tuple,
                unit=unit,
                reset_period=reset_period,
            )
    else:
        assert ImportConsumptionCharge(blocks=blocks_tuple, unit=unit, reset_period=reset_period)


@pytest.mark.parametrize(
    "blocks_tuple, unit, reset_period, raises",
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
            None,
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
            None,
            True,
        ),
    ],
)
def test_export_consumption_charge_must_export(
    blocks_tuple: tuple[ConsumptionBlock, ...],
    unit: ConsumptionUnit | DemandUnit | None,
    reset_period: ResetPeriod,
    raises: bool,
) -> None:
    """"""
    if raises:
        with pytest.raises(ValidationError):
            ExportConsumptionCharge(
                blocks=blocks_tuple,
                unit=unit,
                reset_period=reset_period,
            )
    else:
        assert ExportConsumptionCharge(blocks=blocks_tuple, unit=unit, reset_period=reset_period)


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
                reset_period=ConsumptionResetPeriod.ANNUALLY,
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
                reset_period=ConsumptionResetPeriod.ANNUALLY,
            ),
            ConsumptionCharge(  # expected
                blocks=(ConsumptionBlock(rate=None, from_quantity=50, to_quantity=100),),
                unit=ConsumptionUnit(
                    metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                ),
                reset_period=None,
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
                reset_period=ConsumptionResetPeriod.ANNUALLY,
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
                reset_period=ConsumptionResetPeriod.ANNUALLY,
            ),
            ConsumptionCharge(  # expected
                blocks=(ConsumptionBlock(rate=None, from_quantity=50, to_quantity=100),),
                unit=ConsumptionUnit(
                    metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                ),
                reset_period=None,
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
                reset_period=ConsumptionResetPeriod.ANNUALLY,
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
                reset_period=ConsumptionResetPeriod.ANNUALLY,
            ),
            ConsumptionCharge(  # expected
                blocks=(ConsumptionBlock(rate=None, from_quantity=50, to_quantity=100),),
                unit=ConsumptionUnit(
                    metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                ),
                reset_period=None,
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
                reset_period=ConsumptionResetPeriod.ANNUALLY,
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
                reset_period=ConsumptionResetPeriod.ANNUALLY,
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
                reset_period=ConsumptionResetPeriod.ANNUALLY,
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
                reset_period=ConsumptionResetPeriod.ANNUALLY,
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
                reset_period=ConsumptionResetPeriod.ANNUALLY,
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
                reset_period=ConsumptionResetPeriod.ANNUALLY,
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
                reset_period=None,
            ),
        ),
    ],
)
def test_consumption_charge_intersection_method(
    charge_a: ConsumptionCharge,
    charge_b: ConsumptionCharge | TariffCharge,
    expected_intersection: ConsumptionCharge | None,
) -> None:
    assert (charge_a & charge_b) == expected_intersection


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
                reset_period=ConsumptionResetPeriod.ANNUALLY,
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
                reset_period=ConsumptionResetPeriod.ANNUALLY,
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
                reset_period=ConsumptionResetPeriod.ANNUALLY,
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
                reset_period=ConsumptionResetPeriod.ANNUALLY,
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
                reset_period=ConsumptionResetPeriod.ANNUALLY,
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
                reset_period=ConsumptionResetPeriod.ANNUALLY,
            ),
            False,
        ),
        (  # different reset_periods
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
                reset_period=ConsumptionResetPeriod.ANNUALLY,
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
                reset_period=ConsumptionResetPeriod.DAILY,
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
