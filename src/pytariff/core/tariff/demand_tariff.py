from pydantic import model_validator
from pytariff.core.charge import DemandCharge
from pytariff.core.dataframe.profile import MeterProfileHandler
from pytariff.core.typing import Demand
from pytariff.core.interval import DemandInterval
from pytariff.core.tariff import GenericTariff
import pandas as pd


class DemandTariff(GenericTariff[Demand]):
    """A ``DemandTariff`` is a subclass of a :ref:`generic_tariff`, with the added restrictions:

    * At least one child :ref:`tariff_interval`` must be defined.
    * The child :ref:`tariff_interval` must use :ref:`demand` units (*e.g.* kW)

    There are no restrictions preventing each child ``TariffInterval`` in the ``DemandTariff`` from containing
    multiple :ref:`tariff_block`, and no restriction on the existence of reset periods.
    """

    children: tuple[DemandInterval, ...]

    @model_validator(mode="after")
    def validate_demand_tariff(self) -> "DemandTariff":
        """Assert that the ``DemandTariff`` instance abides by the conditions listed above."""
        if len(self.children) < 1:
            raise ValueError

        for child in self.children:
            if not issubclass(DemandCharge, type(child.charge)):
                raise ValueError

        return self

    def apply_to(self, profile_handler: MeterProfileHandler) -> pd.DataFrame:
        return super().apply_to(profile_handler)
