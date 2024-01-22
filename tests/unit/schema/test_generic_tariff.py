from datetime import datetime, time, timedelta, timezone

from utal._internal.charge import TariffCharge
from utal._internal.day_type import DayType
from utal._internal.days_applied import DaysApplied
from utal.schema.generic_tariff import GenericTariff
from utal._internal.generic_types import Consumption, SignConvention, TradeDirection
from utal._internal.period import ConsumptionResetPeriod
from utal._internal.tariff_interval import TariffInterval
from utal._internal.unit import TariffUnit


def test_generic_tariff_valid_construction(DEFAULT_CONSUMPTION_BLOCK):
    """TODO"""

    GenericTariff(
        start=datetime(2023, 1, 1),
        end=datetime(2023, 12, 31),
        tzinfo=timezone(timedelta(hours=1)),
        children=(
            TariffInterval(
                start_time=time(6),
                end_time=time(12),
                days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
                charge=TariffCharge(
                    blocks=(DEFAULT_CONSUMPTION_BLOCK,),
                    unit=TariffUnit(
                        metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                    ),
                    reset_period=ConsumptionResetPeriod.ANNUALLY,
                ),
                tzinfo=timezone(timedelta(hours=1)),
            ),
        ),
    )
