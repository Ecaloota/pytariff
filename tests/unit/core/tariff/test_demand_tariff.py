from datetime import datetime, time
from typing import Any
from zoneinfo import ZoneInfo
from pydantic import ValidationError
import pytest

from pytariff.core.block import ConsumptionBlock, DemandBlock
from pytariff.core.charge import ConsumptionCharge, DemandCharge
from pytariff.core.day import DayType, DaysApplied
from pytariff.core.typing import Consumption, Demand
from pytariff.core.reset import ResetData, ResetPeriod
from pytariff.core.rate import TariffRate

from pytariff.core.interval import ConsumptionInterval, DemandInterval
from pytariff.core.unit import ConsumptionUnit, DemandUnit, UsageChargeMethod, SignConvention, TradeDirection
from pytariff.core.tariff import DemandTariff


@pytest.mark.parametrize(
    "children, raises",
    [
        ((), True),  # At least one valid child must be provided
        (
            (
                DemandInterval(
                    start_time=time(0, 0),
                    end_time=time(23, 59),
                    days_applied=DaysApplied(day_types=(DayType.ALL_DAYS,)),
                    tzinfo=ZoneInfo("UTC"),
                    charge=DemandCharge(
                        blocks=(
                            DemandBlock(
                                rate=TariffRate(currency="AUD", value=1.0),
                                from_quantity=0,
                                to_quantity=100,
                            ),
                            DemandBlock(
                                rate=TariffRate(currency="AUD", value=2.0),
                                from_quantity=100,
                                to_quantity=float("inf"),
                            ),
                        ),
                        unit=DemandUnit(
                            metric=Demand.kW, direction=TradeDirection.Import, convention=SignConvention.Passive
                        ),
                        reset_data=ResetData(
                            anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY
                        ),
                        method=UsageChargeMethod.mean,
                        resolution="5min",
                        window=None,
                    ),
                ),
            ),
            False,
        ),
        (  # intervals must be valid DemandIntervals
            (
                ConsumptionInterval(
                    start_time=time(0, 0),
                    end_time=time(23, 59),
                    days_applied=DaysApplied(day_types=(DayType.ALL_DAYS,)),
                    tzinfo=ZoneInfo("UTC"),
                    charge=ConsumptionCharge(
                        blocks=(
                            ConsumptionBlock(
                                rate=TariffRate(currency="AUD", value=1.0),
                                from_quantity=0,
                                to_quantity=100,
                            ),
                            ConsumptionBlock(
                                rate=TariffRate(currency="AUD", value=2.0),
                                from_quantity=100,
                                to_quantity=float("inf"),
                            ),
                        ),
                        unit=ConsumptionUnit(
                            metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                        ),
                        reset_data=ResetData(
                            anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY
                        ),
                        method=UsageChargeMethod.mean,
                        resolution="5min",
                        window=None,
                    ),
                ),
            ),
            True,
        ),
    ],
)
def test_demand_tariff_valid_construction(children: Any, raises: bool) -> None:
    """"""

    if raises:
        with pytest.raises(ValidationError):
            DemandTariff(
                start=datetime(2023, 1, 1), end=datetime(2024, 1, 1), tzinfo=ZoneInfo("UTC"), children=children
            )

    else:
        assert DemandTariff(
            start=datetime(2023, 1, 1), end=datetime(2024, 1, 1), tzinfo=ZoneInfo("UTC"), children=children
        )
