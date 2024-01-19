from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
import pandas as pd

from pydantic import ValidationError
from utal.schema.block import ConsumptionBlock
from utal.schema.charge import ConsumptionCharge
from utal.schema.day_type import DayType
from utal.schema.days_applied import DaysApplied
from utal.schema.generic_tariff import ConsumptionTariff
from utal.schema.generic_types import Consumption, TradeDirection
from utal.schema.period import ConsumptionResetPeriod
from utal.schema.rate import TariffRate
from utal.schema.tariff_interval import ConsumptionInterval
import pytest

from utal.schema.unit import ConsumptionUnit, RateCurrency


@pytest.mark.parametrize(
    "block_fixture, raises", [("DEFAULT_CONSUMPTION_BLOCK", False), ("DEFAULT_DEMAND_BLOCK", True)]
)
def test_consumption_tariff_valid_construction(block_fixture: str, raises: bool, request: pytest.FixtureRequest):
    """TODO"""

    block = request.getfixturevalue(block_fixture)

    if raises:
        with pytest.raises(ValidationError):
            ConsumptionTariff(
                start=datetime(2023, 1, 1),
                end=datetime(2023, 12, 31),
                tzinfo=timezone(timedelta(hours=1)),
                children=(
                    ConsumptionInterval(
                        start_time=time(6),
                        end_time=time(12),
                        days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
                        charge=ConsumptionCharge(blocks=(block,)),
                        tzinfo=timezone(timedelta(hours=1)),
                    ),
                ),
                reset_period=ConsumptionResetPeriod.ANNUALLY,
            )

    else:
        assert ConsumptionTariff(
            start=datetime(2023, 1, 1),
            end=datetime(2023, 12, 31),
            tzinfo=timezone(timedelta(hours=1)),
            children=(
                ConsumptionInterval(
                    start_time=time(6),
                    end_time=time(12),
                    days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
                    charge=ConsumptionCharge(blocks=(block,)),
                    tzinfo=timezone(timedelta(hours=1)),
                ),
            ),
            reset_period=ConsumptionResetPeriod.ANNUALLY,
        )


def test_consumption_tariff_apply_method():
    """"""

    meter_profile = pd.DataFrame(
        index=[
            pd.Timestamp(2023, 1, 1, tzinfo=ZoneInfo("UTC"), unit="us"),
            pd.Timestamp(2023, 1, 2, tzinfo=ZoneInfo("UTC"), unit="us"),
        ],
        data={"profile": [1.0, 1.0]},
    )

    tariff = ConsumptionTariff(
        start=datetime(2023, 1, 1),
        end=datetime(2023, 12, 31),
        tzinfo=ZoneInfo("UTC"),
        children=(
            ConsumptionInterval(
                start_time=time(0),
                end_time=time(0),
                days_applied=DaysApplied(day_types=(DayType.ALL_DAYS,)),
                charge=ConsumptionCharge(
                    blocks=(
                        ConsumptionBlock(
                            from_quantity=0,
                            to_quantity=float("inf"),
                            unit=ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
                            rate=TariffRate(currency=RateCurrency.AUD, value=1),
                        ),
                    )
                ),
                tzinfo=timezone(timedelta(hours=1)),
            ),
        ),
        reset_period=ConsumptionResetPeriod.ANNUALLY,
    )

    cost_schema = tariff.apply(meter_profile, billing_start=None)
    print("foo")
