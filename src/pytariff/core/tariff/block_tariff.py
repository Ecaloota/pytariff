import pandas as pd
from pydantic import model_validator
import pandera as pa
from pytariff.core.dataframe.profile import MeterProfileHandler
from pytariff.core.typing import MetricType
from pytariff.core.interval import TariffInterval
from pytariff.core.unit import TariffUnit
from pytariff.core.tariff import GenericTariff


class BlockTariff(GenericTariff[MetricType]):
    """A BlockTariff is a subclass of a GenericTariff that enforces that, among other things:
        1. At least one child TariffInterval must be defined
        2. The child TariffInterval(s) must each contain more than a single non-overlapping block

    There are no restrictions on the units of the child TariffIntervals or the existence of reset periods."""

    children: tuple[TariffInterval[MetricType], ...]

    @model_validator(mode="after")
    def validate_block_tariff(self) -> "BlockTariff":
        if len(self.children) < 1:
            raise ValueError

        for child in self.children:
            if len(child.charge.blocks) < 2:
                raise ValueError

        return self

    @pa.check_types
    def apply_to(self, profile_handler: MeterProfileHandler, profile_unit: TariffUnit) -> pd.DataFrame:
        return super().apply_to(profile_handler, profile_unit)
