from typing import Generic
import pandas as pd
from pydantic import model_validator
from pytariff.core.dataframe.profile import MeterProfileHandler
from pytariff.core.typing import MetricType

from pytariff.core.interval import TariffInterval
from pytariff.core.unit import TariffUnit
from pytariff.core.tariff import GenericTariff


class SingleRateTariff(GenericTariff, Generic[MetricType]):
    """A SingleRateTariff is distinguished from a GenericTariff by having greater
    restrictions on its children; specifically, a SingleRateTariff should have
    at least a single TariffInterval and no more than two TariffIntervals, each of which must contain
    maximum one TariffBlock. If two TariffIntervals are given, their TariffCharges must
    be defined on opposite TradeDirections (Import and Export). Each TariffBlock in each
    TariffInterval must have from_quantity = 0 and to_quantity = float("inf")"""

    children: tuple[TariffInterval[MetricType], ...]

    @model_validator(mode="after")
    def validate_single_rate_tariff(self) -> "SingleRateTariff":
        # Assert we have at least one and at most 2 TariffIntervals
        if not (1 <= len(self.children) <= 2):
            raise ValueError

        for child in self.children:
            if len(child.charge.blocks) != 1:
                raise ValueError

            if child.charge.blocks[0].from_quantity != 0 or child.charge.blocks[0].to_quantity != float("inf"):
                raise ValueError

        # If two children, assert they have opposite TradeDirection
        if len(self.children) == 2:
            if len(set([a.charge.unit.direction for a in self.children])) != 2:
                raise ValueError

        return self

    def apply_to(self, profile_handler: MeterProfileHandler, tariff_unit: TariffUnit) -> pd.DataFrame:
        return super().apply_to(profile_handler, tariff_unit)
