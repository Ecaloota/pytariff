from pydantic import model_validator
from pytariff.core.charge import DemandCharge
from pytariff.core.dataframe.profile import MeterProfileHandler
from pytariff.core.typing import Demand
from pytariff.core.interval import DemandInterval
from pytariff.core.unit import TariffUnit
from pytariff.core.tariff import GenericTariff
import pandas as pd


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

    def apply_to(self, profile_handler: MeterProfileHandler, profile_unit: TariffUnit) -> pd.DataFrame:
        return super().apply_to(profile_handler, profile_unit)
