from datetime import datetime, time
from typing import Any
from zoneinfo import ZoneInfo
from pydantic import ValidationError

import pytest
from utal.core.block import TariffBlock
from utal.core.charge import TariffCharge
from utal.core.day import DayType, DaysApplied
from utal.core.typing import Consumption
from utal.core.reset import ResetData, ResetPeriod
from utal.core.rate import TariffRate, RateCurrency
from utal.core.interval import TariffInterval
from utal.core.unit import TariffUnit, UsageChargeMethod, SignConvention, TradeDirection
from utal.core.tariff import BlockTariff


@pytest.mark.parametrize(
    "children, raises",
    [
        ((), True),  # At least one valid child must be provided
        (
            (
                TariffInterval(
                    start_time=time(0, 0),
                    end_time=time(23, 59),
                    days_applied=DaysApplied(day_types=(DayType.ALL_DAYS,)),
                    tzinfo=ZoneInfo("UTC"),
                    charge=TariffCharge(
                        blocks=(
                            TariffBlock(
                                rate=TariffRate(currency=RateCurrency.AUD, value=1.0),
                                from_quantity=0,
                                to_quantity=100,
                            ),
                            TariffBlock(
                                rate=TariffRate(currency=RateCurrency.AUD, value=2.0),
                                from_quantity=100,
                                to_quantity=float("inf"),
                            ),
                        ),
                        unit=TariffUnit(
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
            False,
        ),
        (  # children must contain more than a single non-overlapping block
            (
                TariffInterval(
                    start_time=time(0, 0),
                    end_time=time(23, 59),
                    days_applied=DaysApplied(day_types=(DayType.ALL_DAYS,)),
                    tzinfo=ZoneInfo("UTC"),
                    charge=TariffCharge(
                        blocks=(
                            TariffBlock(
                                rate=TariffRate(currency=RateCurrency.AUD, value=1.0),
                                from_quantity=0,
                                to_quantity=float("inf"),
                            ),
                        ),
                        unit=TariffUnit(
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
def test_block_tariff_valid_construction(children: Any, raises: bool) -> None:
    """"""

    if raises:
        with pytest.raises(ValidationError):
            BlockTariff(start=datetime(2023, 1, 1), end=datetime(2024, 1, 1), tzinfo=ZoneInfo("UTC"), children=children)

    else:
        assert BlockTariff(
            start=datetime(2023, 1, 1), end=datetime(2024, 1, 1), tzinfo=ZoneInfo("UTC"), children=children
        )
