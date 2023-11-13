from datetime import time, timedelta, timezone

from utal.schema.charge import TariffCharge
from utal.schema.day_type import DayType
from utal.schema.days_applied import DaysApplied
from utal.schema.tariff_interval import TariffInterval


def test_tariff_interval_valid_construction(DEFAULT_BLOCK):
    TariffInterval(
        start_time=time(6),
        end_time=time(12),
        days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
        charge=TariffCharge(blocks=(DEFAULT_BLOCK,)),
        tzinfo=timezone(timedelta(hours=1)),
    )
