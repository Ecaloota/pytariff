from utal.schema.block import TariffBlock
from utal.schema.charge import TariffCharge
from utal.schema.generic_types import Consumption, TradeDirection
from utal.schema.period import ConsumptionResetPeriod
from utal.schema.rate import TariffRate
from utal.schema.unit import RateCurrency, TariffUnit


def test_tariff_charge_valid_construction():
    """Assert that it is possible to generate a valid instance of a TariffCharge, noting
    that it is not possible to instantiate the generic TariffUnit without a specific MetricType
    Unit or without a specific MetricType ResetPeriod"""

    TariffCharge(
        blocks=(
            TariffBlock(
                from_quantity=0,
                to_quantity=float("inf"),
                rate=TariffRate(currency=RateCurrency.AUD, value=1),
            ),
        ),
        unit=TariffUnit(metric=Consumption.kWh, direction=TradeDirection.Import),
        reset_period=ConsumptionResetPeriod.ANNUALLY,
    ),
