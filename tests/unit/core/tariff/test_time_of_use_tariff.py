from datetime import datetime, time
from typing import Any
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
from pydantic import ValidationError
import pytest

from utal.core.block import ConsumptionBlock, TariffBlock
from utal.core.charge import TariffCharge
from utal.core.dataframe.profile import MeterProfileHandler
from utal.core.day import DayType, DaysApplied
from utal.core.typing import Consumption
from utal.core.unit import TradeDirection, SignConvention
from utal.core.reset import ResetData, ResetPeriod
from utal.core.rate import TariffRate

from utal.core.interval import TariffInterval
from utal.core.unit import TariffUnit, UsageChargeMethod
from utal.core.tariff import TimeOfUseTariff
from utal.core.dataframe.cost import TariffCostHandler


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
                                rate=TariffRate(currency="AUD", value=1.0),
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
                                rate=TariffRate(currency="AUD", value=1.0),
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
                                rate=TariffRate(currency="AUD", value=1.0),
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
                                rate=TariffRate(currency="AUD", value=1.0),
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
                                rate=TariffRate(currency="AUD", value=1.0),
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
                                rate=TariffRate(currency="AUD", value=1.0),
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
                                rate=TariffRate(currency="AUD", value=1.0),
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
                                rate=TariffRate(currency="AUD", value=1.0),
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


def test_time_of_use_tariff_apply_to():
    IMPORT_TOU = TariffInterval(
        start_time=time(0),
        end_time=time(0),
        days_applied=DaysApplied(day_types=(DayType.ALL_DAYS,)),
        tzinfo=ZoneInfo("UTC"),
        charge=TariffCharge(
            blocks=(
                TariffBlock(rate=TariffRate(currency="AUD", value=20.0), from_quantity=0.0, to_quantity=float("inf")),
            ),
            unit=TariffUnit(metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive),
            reset_data=None,
            method=UsageChargeMethod.identity,
        ),
    )

    EXPORT_TOU = TariffInterval(
        start_time=time(0),
        end_time=time(0),
        days_applied=DaysApplied(day_types=(DayType.ALL_DAYS,)),
        tzinfo=ZoneInfo("UTC"),
        charge=TariffCharge(
            blocks=(
                TariffBlock(rate=TariffRate(currency="AUD", value=-1.0), from_quantity=0.0, to_quantity=float("inf")),
            ),
            unit=TariffUnit(metric=Consumption.kWh, direction=TradeDirection.Export, convention=SignConvention.Passive),
            reset_data=None,
            method=UsageChargeMethod.identity,
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

    handler = MeterProfileHandler(meter_profile)
    cost_df = tariff.apply_to(  # noqa
        handler,
        tariff_unit=TariffUnit(metric=Consumption.kWh, convention=SignConvention.Passive),
    )

    cost_handler = TariffCostHandler(cost_df)  # noqa
    # cost_handler.plot(include_additional_cost_components=False)
