from datetime import datetime, time, timedelta, timezone

from utal.schema.charge import TariffCharge
from utal.schema.day_type import DayType
from utal.schema.days_applied import DaysApplied
from utal.schema.generic_tariff import GenericTariff
from utal.schema.tariff_interval import TariffInterval


def test_generic_tariff_valid_construction(DEFAULT_BLOCK):
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
                charge=TariffCharge(blocks=(DEFAULT_BLOCK,)),
                tzinfo=timezone(timedelta(hours=1)),
            ),
        ),
    )
