from datetime import datetime, time
from typing import Any
from zoneinfo import ZoneInfo
from pydantic import ValidationError

import pytest
from utal._internal.block import TariffBlock
from utal._internal.charge import TariffCharge
from utal._internal.day_type import DayType
from utal._internal.days_applied import DaysApplied
from utal._internal.generic_types import Demand, SignConvention, TradeDirection
from utal._internal.period import DemandResetPeriod
from utal._internal.rate import TariffRate
from utal._internal.tariff_interval import TariffInterval
from utal._internal.unit import RateCurrency, TariffUnit, UsageChargeMetric

from utal.schema.single_rate_tariff import SingleRateTariff


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
                            metric=Demand.kW, direction=TradeDirection.Import, convention=SignConvention.Passive
                        ),
                        reset_period=DemandResetPeriod.DAILY,
                        method=UsageChargeMetric.mean,
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
                                rate=TariffRate(currency=RateCurrency.AUD, value=2.0),
                                from_quantity=0,
                                to_quantity=float("inf"),
                            ),
                        ),
                        unit=TariffUnit(
                            metric=Demand.kW, direction=TradeDirection.Import, convention=SignConvention.Passive
                        ),
                        reset_period=DemandResetPeriod.DAILY,
                        method=UsageChargeMetric.mean,
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
                                rate=TariffRate(currency=RateCurrency.AUD, value=2.0),
                                from_quantity=0,
                                to_quantity=float("inf"),
                            ),
                        ),
                        unit=TariffUnit(
                            metric=Demand.kW, direction=TradeDirection.Import, convention=SignConvention.Passive
                        ),
                        reset_period=DemandResetPeriod.DAILY,
                        method=UsageChargeMetric.mean,
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
                                rate=TariffRate(currency=RateCurrency.AUD, value=2.0),
                                from_quantity=0,
                                to_quantity=float("inf"),
                            ),
                        ),
                        unit=TariffUnit(
                            metric=Demand.kW, direction=TradeDirection.Export, convention=SignConvention.Passive
                        ),
                        reset_period=DemandResetPeriod.DAILY,
                        method=UsageChargeMetric.mean,
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
