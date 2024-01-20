from pydantic import ValidationError
import pytest

from utal.schema.block import ConsumptionBlock, DemandBlock, TariffBlock
from utal.schema.charge import ConsumptionCharge
from utal.schema.generic_types import Consumption, Demand, TradeDirection
from utal.schema.period import ConsumptionResetPeriod, DemandResetPeriod, ResetPeriod
from utal.schema.rate import TariffRate
from utal.schema.unit import ConsumptionUnit, DemandUnit, RateCurrency


# TODO update this to account for the change in charge definition
# addition of reset period and unit
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
            ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
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
            ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
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
            ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
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
            ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
            None,
            False,
        ),
        (
            (  # parameterized generics can't be used in the isinstance validation check
                TariffBlock[Consumption](
                    rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    from_quantity=0,
                    to_quantity=100,
                ),
            ),
            ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
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
            DemandUnit(metric=Demand.kW, direction=TradeDirection.Import),
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
            ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
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
            ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
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
    """"""
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
                    unit=ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
                    rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    from_quantity=0,
                    to_quantity=101,
                ),
                ConsumptionBlock(
                    unit=ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
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
