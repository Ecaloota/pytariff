from datetime import datetime, time
from typing import Any
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
from pydantic import ValidationError
import pytest
from utal._internal.block import ConsumptionBlock, TariffBlock
from utal._internal.charge import TariffCharge
from utal._internal.day_type import DayType
from utal._internal.days_applied import DaysApplied
from utal._internal.generic_types import Consumption, SignConvention, TradeDirection
from utal._internal.period import ResetData, ResetPeriod
from utal._internal.rate import TariffRate

from utal._internal.tariff_interval import TariffInterval
from utal._internal.unit import TariffUnit, UsageChargeMethod
from utal._internal.currency import RateCurrency
from utal.schema.time_of_use_tariff import TimeOfUseTariff


@pytest.mark.parametrize(
    "children, raises",
    [
        ((), True),  # At least more than one valid child must be provided
        (
            (
                TariffInterval(
                    start_time=time(0, 0),
                    end_time=time(12, 0),
                    days_applied=DaysApplied(day_types=(DayType.ALL_DAYS,)),
                    tzinfo=ZoneInfo("UTC"),
                    charge=TariffCharge(
                        blocks=(
                            ConsumptionBlock(
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
                        window=None,
                    ),
                ),
                TariffInterval(
                    start_time=time(12, 0),
                    end_time=time(23, 59),
                    days_applied=DaysApplied(day_types=(DayType.ALL_DAYS,)),
                    tzinfo=ZoneInfo("UTC"),
                    charge=TariffCharge(
                        blocks=(
                            ConsumptionBlock(
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
                        window=None,
                    ),
                ),
            ),
            False,
        ),
        (  # time interval overlap between child intervals
            (
                TariffInterval(
                    start_time=time(0, 0),
                    end_time=time(23, 59),
                    days_applied=DaysApplied(day_types=(DayType.ALL_DAYS,)),
                    tzinfo=ZoneInfo("UTC"),
                    charge=TariffCharge(
                        blocks=(
                            ConsumptionBlock(
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
                        window=None,
                    ),
                ),
                TariffInterval(
                    start_time=time(12, 0),
                    end_time=time(23, 59),
                    days_applied=DaysApplied(day_types=(DayType.ALL_DAYS,)),
                    tzinfo=ZoneInfo("UTC"),
                    charge=TariffCharge(
                        blocks=(
                            ConsumptionBlock(
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
                        window=None,
                    ),
                ),
            ),
            True,
        ),
        (  # child intervals must share timezone attrs
            (
                TariffInterval(
                    start_time=time(0, 0),
                    end_time=time(12, 0),
                    days_applied=DaysApplied(day_types=(DayType.ALL_DAYS,)),
                    tzinfo=ZoneInfo("Australia/Brisbane"),
                    charge=TariffCharge(
                        blocks=(
                            ConsumptionBlock(
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
                        window=None,
                    ),
                ),
                TariffInterval(
                    start_time=time(12, 0),
                    end_time=time(23, 59),
                    days_applied=DaysApplied(day_types=(DayType.ALL_DAYS,)),
                    tzinfo=ZoneInfo("UTC"),
                    charge=TariffCharge(
                        blocks=(
                            ConsumptionBlock(
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
                        window=None,
                    ),
                ),
            ),
            True,
        ),
        (  # child intervals must share days_applied attrs
            (
                TariffInterval(
                    start_time=time(0, 0),
                    end_time=time(12, 0),
                    days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
                    tzinfo=ZoneInfo("UTC"),
                    charge=TariffCharge(
                        blocks=(
                            ConsumptionBlock(
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
                        window=None,
                    ),
                ),
                TariffInterval(
                    start_time=time(12, 0),
                    end_time=time(23, 59),
                    days_applied=DaysApplied(day_types=(DayType.ALL_DAYS,)),
                    tzinfo=ZoneInfo("UTC"),
                    charge=TariffCharge(
                        blocks=(
                            ConsumptionBlock(
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
                        window=None,
                    ),
                ),
            ),
            True,
        ),
    ],
)
def test_time_of_use_tariff_valid_construction(children: Any, raises: bool) -> None:
    """"""

    if raises:
        with pytest.raises(ValidationError):
            TimeOfUseTariff(
                start=datetime(2023, 1, 1), end=datetime(2024, 1, 1), tzinfo=ZoneInfo("UTC"), children=children
            )

    else:
        assert TimeOfUseTariff(
            start=datetime(2023, 1, 1), end=datetime(2024, 1, 1), tzinfo=ZoneInfo("UTC"), children=children
        )


def test_time_of_use_tariff_apply():
    IMPORT_TOU = TariffInterval(
        start_time=time(0),
        end_time=time(0),
        days_applied=DaysApplied(day_types=(DayType.ALL_DAYS,)),
        tzinfo=ZoneInfo("UTC"),
        charge=TariffCharge(
            blocks=(
                TariffBlock(
                    rate=TariffRate(currency=RateCurrency.AUD, value=20.0), from_quantity=0.0, to_quantity=float("inf")
                ),
            ),
            unit=TariffUnit(metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive),
            reset_data=None,
            method=UsageChargeMethod.cumsum,
        ),
    )

    EXPORT_TOU = TariffInterval(
        start_time=time(0),
        end_time=time(0),
        days_applied=DaysApplied(day_types=(DayType.ALL_DAYS,)),
        tzinfo=ZoneInfo("UTC"),
        charge=TariffCharge(
            blocks=(
                TariffBlock(
                    rate=TariffRate(currency=RateCurrency.AUD, value=-1.0), from_quantity=0.0, to_quantity=float("inf")
                ),
            ),
            unit=TariffUnit(metric=Consumption.kWh, direction=TradeDirection.Export, convention=SignConvention.Passive),
            reset_data=None,
            method=UsageChargeMethod.cumsum,
        ),
    )

    tariff = TimeOfUseTariff(
        start=datetime(2023, 1, 1),
        end=datetime(2024, 1, 1),
        tzinfo=ZoneInfo("UTC"),
        children=(
            IMPORT_TOU,
            EXPORT_TOU,
        ),
    )

    meter_profile = pd.DataFrame(
        index=pd.date_range(
            start="2023-01-01T00:00:00",
            end="2023-01-04T00:00:00",
            tz=ZoneInfo("UTC"),
            freq="1h",
            inclusive="left",
        ),
        data={"profile": np.tile(np.array([0.0] * 8 + [5.0] * 8 + [-1.0] * 8), 3)},
    )

    cost_df = tariff.apply(
        meter_profile,
        tariff_unit=TariffUnit(
            metric=Consumption.kWh, direction=TradeDirection.Export, convention=SignConvention.Passive
        ),
    )

    print("foo")

    # TODO some serious concerns from this test.
    # 1. Costs are levied before profile is non-zero, presumably because the resampling is messing things up
    #   Note for example that the costs always occur 5min before the start of the charge period, presumably when we
    #   resample to 5T
    # 2. Import costs are never applied in the cost_df...
