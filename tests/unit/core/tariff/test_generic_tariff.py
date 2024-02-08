from datetime import datetime, time
from zoneinfo import ZoneInfo

import pytest
import pandas as pd
from pytariff.core.block import TariffBlock

from pytariff.core.charge import TariffCharge
from pytariff.core.dataframe.profile import MeterProfileHandler
from pytariff.core.day import DayType, DaysApplied
from pytariff.core.rate import TariffRate
from pytariff.core.tariff import GenericTariff
from pytariff.core.typing import Consumption
from pytariff.core.reset import ResetData, ResetPeriod
from pytariff.core.interval import TariffInterval
from pytariff.core.unit import ConsumptionUnit, TariffUnit, UsageChargeMethod, SignConvention, TradeDirection


def test_generic_tariff_valid_construction(DEFAULT_CONSUMPTION_BLOCK):
    """TODO"""

    GenericTariff(
        start=datetime(2023, 1, 1),
        end=datetime(2023, 12, 31),
        tzinfo=ZoneInfo("UTC"),
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
                    reset_data=ResetData(
                        anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.FIRST_OF_MONTH
                    ),
                ),
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
def test_generic_tariff_apply_to(profile, import_cost_series, export_cost_series, billed_cost_series):
    """"""

    DEFAULT_CHARGE = TariffCharge(
        blocks=(
            TariffBlock(
                from_quantity=0,
                to_quantity=float("inf"),
                rate=TariffRate(currency="AUD", value=0.998),
            ),
        ),
        unit=ConsumptionUnit(
            metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
        ),
        reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.FIRST_OF_MONTH),
        method=UsageChargeMethod.mean,
    )

    # Create a default single child
    DEFAULT_CHILD = (
        TariffInterval(
            start_time=time(0),
            end_time=time(1),
            days_applied=DaysApplied(day_types=(DayType.ALL_DAYS,)),
            charge=DEFAULT_CHARGE,
        ),
    )

    # Generate a default SingleRateTariff
    DEFAULT_TARIFF = GenericTariff(
        start=datetime(2023, 1, 1),
        end=datetime(2024, 1, 1),
        tzinfo=ZoneInfo("UTC"),
        children=DEFAULT_CHILD,
    )

    handler = MeterProfileHandler(profile)
    output = DEFAULT_TARIFF.apply_to(  # type: ignore  # noqa
        handler,
        profile_unit=TariffUnit(
            metric=Consumption.kWh, direction=TradeDirection._null, convention=SignConvention.Passive
        ),
    )

    # assert output.total_cost == "foo"  # TODO


@pytest.mark.skip("Generates a plot context")
@pytest.mark.parametrize(
    "profile",
    [
        pd.DataFrame(
            index=[
                pd.Timestamp(2023, 1, 1, tzinfo=ZoneInfo("UTC"), unit="ns"),
                pd.Timestamp(2023, 1, 1, 0, 5, tzinfo=ZoneInfo("UTC"), unit="ns"),
            ],
            data={"profile": [1.0, 1.0]},
        ),
    ],
)
def test_generic_tariff_plot(profile):
    """"""

    DEFAULT_CHARGE = TariffCharge(
        blocks=(
            TariffBlock(
                from_quantity=0,
                to_quantity=float("inf"),
                rate=TariffRate(currency="AUD", value=0.998),
            ),
        ),
        unit=ConsumptionUnit(
            metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
        ),
        reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.FIRST_OF_MONTH),
        method=UsageChargeMethod.cumsum,
    )

    # Create a default single child
    DEFAULT_CHILD = (
        TariffInterval(
            start_time=time(0),
            end_time=time(1),
            days_applied=DaysApplied(day_types=(DayType.ALL_DAYS,)),
            charge=DEFAULT_CHARGE,
        ),
    )

    # Generate a default SingleRateTariff
    DEFAULT_TARIFF = GenericTariff(
        start=datetime(2023, 1, 1),
        end=datetime(2024, 1, 1),
        tzinfo=ZoneInfo("UTC"),
        children=DEFAULT_CHILD,
    )

    handler = MeterProfileHandler(profile)
    cost_df = DEFAULT_TARIFF.apply_to(  # type: ignore  # noqa
        handler,
        profile_unit=TariffUnit(
            metric=Consumption.kWh, direction=TradeDirection._null, convention=SignConvention.Passive
        ),
    )

    # plot(cost_df, include_additional_cost_components=True)
    # plot(cost_df, include_additional_cost_components=False)
