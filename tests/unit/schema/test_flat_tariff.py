from datetime import datetime, time
from zoneinfo import ZoneInfo

from utal.schema.block import ConsumptionBlock
from utal.schema.charge import ConsumptionCharge
from utal.schema.day_type import DayType
from utal.schema.days_applied import DaysApplied
from utal.schema.flat_tariff import FlatConsumptionTariff
from utal.schema.rate import TariffRate
from utal.schema.tariff_interval import TariffInterval
from utal.schema.unit import ConsumptionUnit, RateCurrency


# TODO A FlatConsumptionTariff is distinguished from a GenericTariff by having greater
# restrictions on its children; specifically, a FlatConsumptionTariff should have only a single
# TariffInterval, which itself should have a ConsumptionCharge (only) containing (only) one
# ConsumptionBlock; the ConsumptionBlock should have a from_quantity = 0 and to_quantity = float("inf")
def test_flat_consumption_tariff():
    FlatConsumptionTariff(
        start=datetime(2023, 1, 1),
        end=datetime(2023, 12, 31),
        tzinfo=ZoneInfo("Australia/Brisbane"),
        children=(
            TariffInterval(
                start_time=time(6),
                end_time=time(7),
                days_applied=DaysApplied(day_types=(DayType.ALL_DAYS,)),
                tzinfo=ZoneInfo("Australia/Brisbane"),
                charge=ConsumptionCharge(
                    blocks=(
                        ConsumptionBlock(
                            from_quantity=0,
                            to_quantity=float("inf"),
                            unit=ConsumptionUnit.kWh,
                            rate=TariffRate(currency=RateCurrency.AUD, value=1),
                        ),
                    )
                ),
            ),
        ),
    )
