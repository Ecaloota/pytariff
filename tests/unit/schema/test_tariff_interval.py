from datetime import time, timedelta, timezone
from pydantic import ValidationError

import pytest
from utal.schema.block import ConsumptionBlock, DemandBlock

from utal.schema.charge import TariffCharge
from utal.schema.day_type import DayType
from utal.schema.days_applied import DaysApplied
from utal.schema.generic_types import Consumption, TradeDirection
from utal.schema.period import ConsumptionResetPeriod
from utal.schema.rate import TariffRate
from utal.schema.tariff_interval import TariffInterval
from utal.schema.unit import RateCurrency, TariffUnit


@pytest.mark.parametrize(
    "block, is_valid",
    [
        (
            ConsumptionBlock(
                from_quantity=0,
                to_quantity=float("inf"),
                rate=TariffRate(currency=RateCurrency.AUD, value=1),
            ),
            True,
        ),
        (
            DemandBlock(
                from_quantity=0,
                to_quantity=float("inf"),
                rate=TariffRate(currency=RateCurrency.AUD, value=1),
            ),
            True,
        ),
    ],
)
def test_tariff_interval_valid_construction(block, is_valid: bool) -> None:
    if is_valid:
        TariffInterval(
            start_time=time(6),
            end_time=time(12),
            days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
            charge=TariffCharge(
                blocks=(block,),
                unit=TariffUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
                reset_period=ConsumptionResetPeriod.DAILY,
            ),
            tzinfo=timezone(timedelta(hours=1)),
        )
    else:
        with pytest.raises(ValidationError):
            TariffInterval(
                start_time=time(6),
                end_time=time(12),
                days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
                charge=TariffCharge(
                    blocks=(block,),
                    unit=TariffUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
                    reset_period=ConsumptionResetPeriod.DAILY,
                ),
                tzinfo=timezone(timedelta(hours=1)),
            )
