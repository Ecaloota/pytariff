import pandera as pa
from pandera.typing import DataFrame
from pydantic import model_validator
from utal._internal.generic_types import Consumption
from utal._internal.meter_profile import MeterProfileSchema, TariffCostSchema
from utal._internal.tariff_interval import ConsumptionInterval
from utal._internal.unit import TariffUnit
from utal.schema.generic_tariff import GenericTariff


class ConsumptionTariff(GenericTariff[Consumption]):
    """A ConsumptionTariff is a subclass of a GenericTariff that enforces that, among other things:
        1. At least one child TariffInterval must be defined
        2. The child TariffInterval(s) must use Consumption units (e.g. kW)

    There are no restrictions preventing each child TariffInterval in the ConsumptionTariff from containing multiple
    blocks, and no restriction on the existence of reset periods on each TariffInterval.
    """

    children: tuple[ConsumptionInterval, ...]

    @model_validator(mode="after")
    def validate_children_are_consumption_intervals(self) -> "ConsumptionTariff":
        if self.children is not None:
            if not all(isinstance(x, ConsumptionInterval) for x in self.children):
                raise ValueError
        return self

    @pa.check_types
    def apply(
        self, meter_profile: DataFrame[MeterProfileSchema], profile_unit: TariffUnit
    ) -> DataFrame[TariffCostSchema]:
        return super().apply(meter_profile, profile_unit)
