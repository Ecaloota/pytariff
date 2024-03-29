from datetime import datetime, time
from typing import Any
from zoneinfo import ZoneInfo
from pydantic import ValidationError

import pytest
from pytariff.core.block import TariffBlock
from pytariff.core.charge import TariffCharge
from pytariff.core.day import DayType, DaysApplied
from pytariff.core.typing import Demand
from pytariff.core.reset import ResetData, ResetPeriod
from pytariff.core.rate import TariffRate
from pytariff.core.interval import TariffInterval
from pytariff.core.unit import TariffUnit, UsageChargeMethod, SignConvention, TradeDirection

from pytariff.core.tariff import SingleRateTariff


@pytest.mark.parametrize(
    "children, raises",
    [
        (  # must have at least one tariff interval
            (),
            True,
        ),
        (  # Only one block per charge allowed
            (
                TariffInterval(
                    start_time=time(0, 0),
                    end_time=time(23, 59),
                    days_applied=DaysApplied(day_types=(DayType.ALL_DAYS,)),
                    tzinfo=ZoneInfo("UTC"),
                    charge=TariffCharge(
                        blocks=(
                            TariffBlock(
                                rate=TariffRate(currency="AUD", value=1.0),
                                from_quantity=0,
                                to_quantity=100,
                            ),
                            TariffBlock(
                                rate=TariffRate(currency="AUD", value=2.0),
                                from_quantity=100,
                                to_quantity=float("inf"),
                            ),
                        ),
                        unit=TariffUnit(
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
            True,
        ),
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
                                rate=TariffRate(currency="AUD", value=2.0),
                                from_quantity=0,
                                to_quantity=float("inf"),
                            ),
                        ),
                        unit=TariffUnit(
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
        (  # two tariff intervals (each with one block) is allowed with opposite TradeDirections
            (
                TariffInterval(
                    start_time=time(0, 0),
                    end_time=time(23, 59),
                    days_applied=DaysApplied(day_types=(DayType.ALL_DAYS,)),
                    tzinfo=ZoneInfo("UTC"),
                    charge=TariffCharge(
                        blocks=(
                            TariffBlock(
                                rate=TariffRate(currency="AUD", value=2.0),
                                from_quantity=0,
                                to_quantity=float("inf"),
                            ),
                        ),
                        unit=TariffUnit(
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
                TariffInterval(
                    start_time=time(0, 0),
                    end_time=time(23, 59),
                    days_applied=DaysApplied(day_types=(DayType.ALL_DAYS,)),
                    tzinfo=ZoneInfo("UTC"),
                    charge=TariffCharge(
                        blocks=(
                            TariffBlock(
                                rate=TariffRate(currency="AUD", value=2.0),
                                from_quantity=0,
                                to_quantity=float("inf"),
                            ),
                        ),
                        unit=TariffUnit(
                            metric=Demand.kW, direction=TradeDirection.Export, convention=SignConvention.Passive
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
    ],
)
def test_single_rate_tariff_construction(children: Any, raises: bool):
    if raises:
        with pytest.raises(ValidationError):
            SingleRateTariff(
                start=datetime(2023, 1, 1), end=datetime(2024, 1, 1), tzinfo=ZoneInfo("UTC"), children=children
            )

    else:
        assert SingleRateTariff(
            start=datetime(2023, 1, 1), end=datetime(2024, 1, 1), tzinfo=ZoneInfo("UTC"), children=children
        )
