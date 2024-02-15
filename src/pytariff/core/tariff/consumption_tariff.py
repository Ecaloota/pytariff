import pandas as pd
from pydantic import model_validator
from pytariff.core.dataframe.profile import MeterProfileHandler
from pytariff.core.typing import Consumption
from pytariff.core.interval import ConsumptionInterval
from pytariff.core.tariff import GenericTariff


class ConsumptionTariff(GenericTariff[Consumption]):
    """A ``ConsumptionTariff`` is a subclass of a :ref:`generic_tariff`, with the added restrictions:

    * At least one child :ref:`tariff_interval`` must be defined.
    * The child :ref:`tariff_interval` must use :ref:`consumption` units (*e.g.* kWh)

    There are no restrictions preventing each child ``TariffInterval`` in the ``ConsumptionTariff`` from containing
    multiple :ref:`tariff_block`, and no restriction on the existence of reset periods.
    """

    children: tuple[ConsumptionInterval, ...]

    @model_validator(mode="after")
    def validate_children_are_consumption_intervals(self) -> "ConsumptionTariff":
        """Assert that the ``ConsumptionTariff`` instance abides by the conditions listed above."""
        if self.children is not None:
            if not all(isinstance(x, ConsumptionInterval) for x in self.children):
                raise ValueError
        return self

    def apply_to(self, profile_handler: MeterProfileHandler) -> pd.DataFrame:
        return super().apply_to(profile_handler)
