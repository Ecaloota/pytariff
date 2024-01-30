from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
import pandas as pd

from pydantic import ValidationError
from utal._internal.block import ConsumptionBlock
from utal._internal.charge import ConsumptionCharge
from utal._internal.day_type import DayType
from utal._internal.days_applied import DaysApplied
from utal._internal.period import ResetData, ResetPeriod
from utal.schema.consumption_tariff import ConsumptionTariff
from utal._internal.generic_types import Consumption, SignConvention, TradeDirection
from utal._internal.rate import TariffRate
from utal._internal.tariff_interval import ConsumptionInterval
import pytest

from utal._internal.unit import ConsumptionUnit, TariffUnit, UsageChargeMethod
from utal._internal.currency import RateCurrency


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
                        charge=ConsumptionCharge(
                            blocks=(block,),
                            unit=ConsumptionUnit(
                                metric=Consumption.kWh,
                                direction=TradeDirection.Import,
                                convention=SignConvention.Passive,
                            ),
                            reset_data=ResetData(
                                anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY
                            ),
                        ),
                        tzinfo=timezone(timedelta(hours=1)),
                    ),
                ),
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
                    charge=ConsumptionCharge(
                        blocks=(block,),
                        unit=ConsumptionUnit(
                            metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                        ),
                        reset_data=ResetData(
                            anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY
                        ),
                    ),
                    tzinfo=timezone(timedelta(hours=1)),
                ),
            ),
        )


def test_consumption_tariff_apply_method():
    """"""

    meter_profile = pd.DataFrame(
        index=[
            pd.Timestamp(2023, 1, 1, tzinfo=ZoneInfo("UTC"), unit="us"),
            pd.Timestamp(2023, 1, 2, tzinfo=ZoneInfo("UTC"), unit="us"),
        ],
        data={"profile": [1.0, -1.0]},
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
                            rate=TariffRate(currency=RateCurrency.AUD, value=1),
                        ),
                    ),
                    unit=ConsumptionUnit(
                        metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                    ),
                    reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
                    method=UsageChargeMethod.cumsum,
                ),
                tzinfo=ZoneInfo("UTC"),
            ),
        ),
    )

    cost_schema = tariff.apply(  # noqa
        meter_profile,
        profile_unit=TariffUnit(
            metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
        ),
    )  # noqa
    print("foo")
