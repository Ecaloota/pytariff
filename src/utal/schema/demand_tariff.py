from pydantic import model_validator
from utal._internal.charge import DemandCharge
from utal._internal.generic_types import Demand
from utal._internal.meter_profile import MeterProfileSchema, TariffCostSchema
from utal._internal.tariff_interval import DemandInterval
from utal._internal.unit import TariffUnit
from utal.schema.generic_tariff import GenericTariff
import pandera as pa
from pandera.typing import DataFrame


class DemandTariff(GenericTariff[Demand]):
    """A DemandTariff is a subclass of a GenericTariff that enforces that, among other things:
        1. At least one child TariffInterval must be defined
        2. The child TariffInterval(s) must use Demand units (e.g. kW)

    There are no restrictions preventing each child TariffInterval in the DemandTariff from containing multiple
    blocks, and no restriction on the existence of reset periods on each TariffInterval.
    """

    children: tuple[DemandInterval, ...]

    @model_validator(mode="after")
    def validate_demand_tariff(self) -> "DemandTariff":
        if len(self.children) < 1:
            raise ValueError

        for child in self.children:
            if not issubclass(DemandCharge, type(child.charge)):
                raise ValueError

        return self

    @pa.check_types
    def apply(
        self, meter_profile: DataFrame[MeterProfileSchema], profile_unit: TariffUnit
    ) -> DataFrame[TariffCostSchema]:
        return super().apply(meter_profile, profile_unit)
