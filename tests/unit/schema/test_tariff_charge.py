from utal.schema.block import ConsumptionBlock
from utal.schema.charge import TariffCharge
from utal.schema.rate import TariffRate
from utal.schema.unit import ConsumptionUnit, RateCurrency


def test_tariff_charge_valid_construction():
    TariffCharge(
        blocks=(
            ConsumptionBlock(
                from_quantity=0,
                to_quantity=float("inf"),
                unit=ConsumptionUnit.kWh,
                rate=TariffRate(currency=RateCurrency.AUD, value=1),
            ),
        )
    ),
