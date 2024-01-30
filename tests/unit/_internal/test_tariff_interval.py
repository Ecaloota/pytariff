from datetime import time, timedelta, timezone, datetime
from zoneinfo import ZoneInfo
from pydantic import ValidationError

import pytest
from utal._internal.block import ConsumptionBlock, DemandBlock

from utal._internal.charge import ConsumptionCharge, DemandCharge, TariffCharge
from utal._internal.day_type import DayType
from utal._internal.days_applied import DaysApplied
from utal._internal.generic_types import Consumption, Demand, SignConvention, TradeDirection
from utal._internal.period import ResetData, ResetPeriod
from utal._internal.rate import TariffRate
from utal._internal.tariff_interval import ConsumptionInterval, DemandInterval, TariffInterval
from utal._internal.unit import ConsumptionUnit, DemandUnit, TariffUnit
from utal._internal.currency import RateCurrency


@pytest.mark.parametrize(
    "block, is_valid",
    [
        (
            ConsumptionBlock(
                from_quantity=0,
                to_quantity=float("inf"),
                rate=TariffRate(currency=RateCurrency.AUD, value=1),
            ),
            True,
        ),
        (
            DemandBlock(
                from_quantity=0,
                to_quantity=float("inf"),
                rate=TariffRate(currency=RateCurrency.AUD, value=1),
            ),
            True,
        ),
    ],
)
def test_tariff_interval_valid_construction(block: ConsumptionBlock | DemandBlock, is_valid: bool) -> None:
    if is_valid:
        TariffInterval(
            start_time=time(6),
            end_time=time(12),
            days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
            charge=TariffCharge(
                blocks=(block,),
                unit=TariffUnit(
                    metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                ),
                reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            ),
            tzinfo=timezone(timedelta(hours=1)),
        )
    else:
        with pytest.raises(ValidationError):
            TariffInterval(
                start_time=time(6),
                end_time=time(12),
                days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
                charge=TariffCharge(
                    blocks=(block,),
                    unit=TariffUnit(
                        metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                    ),
                    reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
                ),
                tzinfo=timezone(timedelta(hours=1)),
            )


@pytest.mark.parametrize(
    "charge, raises",
    [
        (
            ConsumptionCharge(
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
            ),
            False,
        ),
        (
            DemandCharge(
                blocks=(
                    DemandBlock(
                        from_quantity=0,
                        to_quantity=float("inf"),
                        rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    ),
                ),
                unit=DemandUnit(metric=Demand.kW, direction=TradeDirection.Import, convention=SignConvention.Passive),
                reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            ),
            True,
        ),
    ],
)
def test_consumption_interval_charges_must_be_consumption_charges(
    charge: ConsumptionCharge | DemandCharge, raises: bool
) -> None:
    if raises:
        with pytest.raises(ValidationError):
            ConsumptionInterval(
                start_time=time(6),
                end_time=time(12),
                days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
                charge=charge,
                tzinfo=timezone(timedelta(hours=1)),
            )

    else:
        ConsumptionInterval(
            start_time=time(6),
            end_time=time(12),
            days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
            charge=charge,
            tzinfo=timezone(timedelta(hours=1)),
        )


@pytest.mark.parametrize(
    "charge, raises",
    [
        (
            DemandCharge(
                blocks=(
                    DemandBlock(
                        from_quantity=0,
                        to_quantity=float("inf"),
                        rate=TariffRate(currency=RateCurrency.AUD, value=1),
                    ),
                ),
                unit=DemandUnit(metric=Demand.kW, direction=TradeDirection.Import, convention=SignConvention.Passive),
                reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
            ),
            False,
        ),
        (
            ConsumptionCharge(
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
            ),
            True,
        ),
    ],
)
def test_demand_interval_charges_must_be_demand_charges(charge: ConsumptionCharge | DemandCharge, raises: bool) -> None:
    if raises:
        with pytest.raises(ValidationError):
            DemandInterval(
                start_time=time(6),
                end_time=time(12),
                days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
                charge=charge,
                tzinfo=timezone(timedelta(hours=1)),
            )

    else:
        DemandInterval(
            start_time=time(6),
            end_time=time(12),
            days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
            charge=charge,
            tzinfo=timezone(timedelta(hours=1)),
        )


@pytest.mark.parametrize(
    "interval_a, interval_b, is_equal",
    [
        (
            TariffInterval(
                start_time=time(6),
                end_time=time(12),
                days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
                charge=TariffCharge(
                    blocks=(
                        ConsumptionBlock(
                            from_quantity=0,
                            to_quantity=float("inf"),
                            rate=TariffRate(currency=RateCurrency.AUD, value=1),
                        ),
                    ),
                    unit=TariffUnit(
                        metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                    ),
                    reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
                ),
                tzinfo=timezone(timedelta(hours=1)),
            ),
            TariffInterval(
                start_time=time(6),
                end_time=time(12),
                days_applied=DaysApplied(day_types=(DayType.MONDAY,)),
                charge=TariffCharge(
                    blocks=(
                        ConsumptionBlock(
                            from_quantity=0,
                            to_quantity=float("inf"),
                            rate=TariffRate(currency=RateCurrency.AUD, value=1),
                        ),
                    ),
                    unit=TariffUnit(
                        metric=Consumption.kWh, direction=TradeDirection.Import, convention=SignConvention.Passive
                    ),
                    reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
                ),
                tzinfo=timezone(timedelta(hours=1)),
            ),
            True,
        ),
    ],
)
def test_tariff_interval_hash(interval_a: TariffInterval, interval_b: TariffInterval, is_equal: bool) -> None:
    assert (interval_a == interval_b) is is_equal
    if is_equal:
        assert hash(interval_a) == hash(interval_b)
    else:
        assert hash(interval_a) != hash(interval_b)

    # TODO test the contrapositive
