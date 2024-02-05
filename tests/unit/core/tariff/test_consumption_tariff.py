from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
import pandas as pd

from pydantic import ValidationError
from pytariff.core.block import ConsumptionBlock
from pytariff.core.charge import ConsumptionCharge
from pytariff.core.dataframe.profile import MeterProfileHandler
from pytariff.core.day import DayType, DaysApplied
from pytariff.core.reset import ResetData, ResetPeriod
from pytariff.core.tariff import ConsumptionTariff
from pytariff.core.typing import Consumption
from pytariff.core.unit import ConsumptionUnit, TariffUnit, UsageChargeMethod, SignConvention, TradeDirection
from pytariff.core.rate import TariffRate
from pytariff.core.interval import ConsumptionInterval
import pytest


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


def test_consumption_tariff_apply_to_method():
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
                            rate=TariffRate(currency="AUD", value=1),
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

    handler = MeterProfileHandler(meter_profile)
    cost_schema = tariff.apply_to(  # noqa
        handler,
        profile_unit=TariffUnit(
            metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
        ),
    )  # noqa
    print("foo")
