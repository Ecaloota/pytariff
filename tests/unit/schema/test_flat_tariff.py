from collections import defaultdict
from datetime import datetime, time
from zoneinfo import ZoneInfo

import pytest

from utal.schema.block import ConsumptionBlock, ImportConsumptionBlock
from utal.schema.charge import ConsumptionCharge
from utal.schema.day_type import DayType
from utal.schema.days_applied import DaysApplied
from utal.schema.flat_tariff import FlatConsumptionTariff
from utal.schema.generic_types import Consumption, TradeDirection
from utal.schema.rate import TariffRate
from utal.schema.tariff_interval import ConsumptionInterval
from utal.schema.unit import ConsumptionUnit, RateCurrency

import pandas as pd


def not_in(kwargs: defaultdict, key: str) -> bool:
    """Returns True if key is not present in kwargs and if kwargs[key] does not
    return None"""
    return not kwargs[key] and kwargs[key] is not None


@pytest.mark.parametrize(
    "kwargs, raises",
    [
        (defaultdict(bool, {}), False),
        (defaultdict(bool, {"charge": None}), True),  # charge of None is invalid
        (defaultdict(bool, {"children": None}), True),  # children = None is invalid for FlatConsumptionTariff
        (defaultdict(bool, {"children": ["a", "b"]}), True),  # len(children) > 1 is invalid for FlatConsumptionTariff
        (defaultdict(bool, {"children": "a"}), True),  # children must be ConsumptionIntervals
        (defaultdict(bool, {"charge": "a"}), True),  # children charges must be ConsumptionCharges
        (defaultdict(bool, {"charge": "a"}), True),  # children charges must be ConsumptionCharges
        (defaultdict(bool, {"blocks": None}), True),  # children charge blocks cannot be None
        (defaultdict(bool, {"blocks": "a"}), True),  # children charge blocks must be ConsumptionBlocks
        (defaultdict(bool, {"from_quantity": 1}), True),  # from_quantity in ConsumptionCharge Blocks must be 0
        (defaultdict(bool, {"to_quantity": 1}), True),  # to_quantity in ConsumptionCharge Blocks must be +inf
    ],
)
def test_flat_consumption_tariff_construction(kwargs, raises: bool):
    """"""

    def test() -> FlatConsumptionTariff:
        # Create a default FlatConsumptionTariff ConsumptionCharge
        DEFAULT_CHARGE = ConsumptionCharge(
            blocks=(
                ConsumptionBlock(
                    from_quantity=0 if not_in(kwargs, "from_quantity") else kwargs["from_quantity"],
                    to_quantity=float("inf") if not_in(kwargs, "to_quantity") else kwargs["to_quantity"],
                    unit=ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
                    rate=TariffRate(currency=RateCurrency.AUD, value=1),
                ),
            )
            if not_in(kwargs, "blocks")
            else kwargs["blocks"]
        )

        # Create a default single child
        DEFAULT_CHILD = (
            ConsumptionInterval(
                start_time=time(6) if not_in(kwargs, "start_time") else kwargs["start_time"],
                end_time=time(7) if not_in(kwargs, "end_time") else kwargs["end_time"],
                days_applied=DaysApplied(day_types=(DayType.ALL_DAYS,))
                if not_in(kwargs, "days_applied")
                else kwargs["days_applied"],
                tzinfo=ZoneInfo("UTC") if not_in(kwargs, "tzinfo") else kwargs["tzinfo"],
                charge=DEFAULT_CHARGE if not_in(kwargs, "charge") else kwargs["charge"],
            ),
        )

        # Generate a default FlatConsumptionTariff
        DEFAULT_TARIFF = FlatConsumptionTariff(
            start=datetime(2023, 1, 1) if not_in(kwargs, "start") else kwargs["start"],  # given dt
            end=datetime(2023, 1, 1) if not_in(kwargs, "end") else kwargs["end"],
            tzinfo=ZoneInfo("UTC") if not_in(kwargs, "tzinfo") else kwargs["tzinfo"],
            children=DEFAULT_CHILD if not_in(kwargs, "children") else kwargs["children"],
        )

        return DEFAULT_TARIFF

    if raises:
        with pytest.raises(ValueError):
            test()

    else:
        test()


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
def test_flat_consumption_tariff_apply(profile, import_cost_series, export_cost_series, billed_cost_series):
    """"""

    DEFAULT_CHARGE = ConsumptionCharge(
        blocks=(
            ImportConsumptionBlock(
                from_quantity=0,
                to_quantity=float("inf"),
                unit=ConsumptionUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
                rate=TariffRate(currency=RateCurrency.AUD, value=1),
            ),
            # ExportConsumptionBlock(
            #     from_quantity=0,
            #     to_quantity=float("inf"),
            #     unit=ConsumptionUnit.kWh,
            #     rate=TariffRate(currency=RateCurrency.AUD, value=-0.1),  # value is negative as it's a negative 'cost'
            # ),
        ),
    )

    # Create a default single child
    DEFAULT_CHILD = (
        ConsumptionInterval(
            start_time=time(6),
            end_time=time(7),
            days_applied=DaysApplied(day_types=(DayType.ALL_DAYS,)),
            tzinfo=ZoneInfo("UTC"),
            charge=DEFAULT_CHARGE,
        ),
    )

    # Generate a default FlatConsumptionTariff
    DEFAULT_TARIFF = FlatConsumptionTariff(
        start=datetime(2023, 1, 1),
        end=datetime(2023, 1, 1),
        tzinfo=ZoneInfo("UTC"),
        children=DEFAULT_CHILD,
    )

    output = DEFAULT_TARIFF.apply(profile)  # noqa

    # assert output.total_cost == "foo"  # TODO
