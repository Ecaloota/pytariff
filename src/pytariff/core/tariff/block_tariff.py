import pandas as pd
from pydantic import model_validator
import pandera as pa
from pytariff.core.dataframe.profile import MeterProfileHandler
from pytariff.core.typing import MetricType
from pytariff.core.interval import TariffInterval
from pytariff.core.tariff import GenericTariff


class BlockTariff(GenericTariff[MetricType]):
    """A BlockTariff is a subclass of a :ref:`generic_tariff`, with the added restrictions:

    * At least one child :ref:`tariff_interval` must be defined
    * The child :ref:`tariff_interval` must each contain more than a single non-overlapping :ref:`tariff_block`

    There are no restrictions on the units of the child ``TariffInterval`` or the existence of reset periods.
    """

    children: tuple[TariffInterval[MetricType], ...]

    @model_validator(mode="after")
    def validate_block_tariff(self) -> "BlockTariff":
        """Assert that the ``BlockTariff`` instance abides by the conditions listed above."""

        if len(self.children) < 1:
            raise ValueError

        for child in self.children:
            if len(child.charge.blocks) < 2:
                raise ValueError

        return self

    @pa.check_types
    def apply_to(self, profile_handler: MeterProfileHandler) -> pd.DataFrame:
        return super().apply_to(profile_handler)
