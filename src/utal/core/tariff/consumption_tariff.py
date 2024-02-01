import pandas as pd
from pydantic import model_validator
from utal.core.dataframe.profile import MeterProfileHandler
from utal.core.typing import Consumption
from utal.core.interval import ConsumptionInterval
from utal.core.unit import TariffUnit
from utal.core.tariff import GenericTariff


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

    def apply_to(self, profile_handler: MeterProfileHandler, profile_unit: TariffUnit) -> pd.DataFrame:
        return super().apply_to(profile_handler, profile_unit)
