from datetime import datetime, time, timedelta, timezone

from utal.schema.charge import TariffCharge
from utal.schema.day_type import DayType
from utal.schema.days_applied import DaysApplied
from utal.schema.generic_tariff import GenericTariff
from utal.schema.generic_types import Consumption, TradeDirection
from utal.schema.period import ConsumptionResetPeriod
from utal.schema.tariff_interval import TariffInterval
from utal.schema.unit import TariffUnit


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
                    unit=TariffUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
                    reset_period=ConsumptionResetPeriod.ANNUALLY,
                ),
                tzinfo=timezone(timedelta(hours=1)),
            ),
        ),
    )
