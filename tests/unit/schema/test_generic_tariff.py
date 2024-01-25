from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest
import pandas as pd
from utal._internal.block import TariffBlock

from utal._internal.charge import TariffCharge
from utal._internal.day_type import DayType
from utal._internal.days_applied import DaysApplied
from utal._internal.rate import TariffRate
from utal.schema.generic_tariff import GenericTariff
from utal._internal.generic_types import Consumption, SignConvention, TradeDirection
from utal._internal.period import ConsumptionResetPeriod
from utal._internal.tariff_interval import TariffInterval
from utal._internal.unit import ConsumptionUnit, RateCurrency, TariffUnit


def test_generic_tariff_valid_construction(DEFAULT_CONSUMPTION_BLOCK):
    """TODO"""

    GenericTariff(
        start=datetime(2023, 1, 1),
        end=datetime(2023, 12, 31),
        tzinfo=timezone(timedelta(hours=1)),
        children=(
            TariffInterval(
                start_time=time(6),
                end_time=time(12),
                days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
                charge=TariffCharge(
                    blocks=(DEFAULT_CONSUMPTION_BLOCK,),
                    unit=TariffUnit(
                        metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                    ),
                    reset_period=ConsumptionResetPeriod.ANNUALLY,
                ),
                tzinfo=timezone(timedelta(hours=1)),
            ),
        ),
    )


@pytest.mark.parametrize(
    "profile, import_cost_series, export_cost_series, billed_cost_series",
    [
        (
            pd.DataFrame(
                index=[
                    pd.Timestamp(2023, 1, 1, tzinfo=ZoneInfo("UTC"), unit="ns"),
                    pd.Timestamp(2023, 1, 1, 0, 5, tzinfo=ZoneInfo("UTC"), unit="ns"),
                ],
                data={"profile": [1.0, 1.0]},
            ),
            None,
            None,
            None,
        ),
        (
            pd.DataFrame(
                index=[
                    pd.Timestamp(2023, 1, 1, tzinfo=ZoneInfo("UTC"), unit="ns"),
                    pd.Timestamp(2023, 1, 1, 0, 5, tzinfo=ZoneInfo("UTC"), unit="ns"),
                ],
                data={"profile": [1.0, 1.0]},
            ),
            None,
            None,
            None,
        ),
    ],
)
def test_generic_tariff_apply(profile, import_cost_series, export_cost_series, billed_cost_series):
    """"""

    DEFAULT_CHARGE = TariffCharge(
        blocks=(
            TariffBlock(
                from_quantity=0,
                to_quantity=float("inf"),
                rate=TariffRate(currency=RateCurrency.AUD, value=1),
            ),
        ),
        unit=ConsumptionUnit(
            metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
        ),
        reset_period=None,
    )

    # Create a default single child
    DEFAULT_CHILD = (
        TariffInterval(
            start_time=time(0),
            end_time=time(1),
            days_applied=DaysApplied(day_types=(DayType.ALL_DAYS,)),
            tzinfo=ZoneInfo("UTC"),
            charge=DEFAULT_CHARGE,
        ),
    )

    # Generate a default SingleRateTariff
    DEFAULT_TARIFF = GenericTariff(
        start=datetime(2023, 1, 1),
        end=datetime(2024, 1, 1),
        tzinfo=ZoneInfo("UTC"),
        children=DEFAULT_CHILD,
        reset_period=ConsumptionResetPeriod.ANNUALLY,
    )

    output = DEFAULT_TARIFF.apply(
        meter_profile=profile,
        billing_start=None,
        profile_unit=TariffUnit(
            metric=Consumption.kWh, direction=TradeDirection._null, convention=SignConvention.Passive
        ),
    )  # noqa

    # assert output.total_cost == "foo"  # TODO
