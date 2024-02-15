from typing import Generic
import pandas as pd
from pydantic import model_validator
from pytariff.core.dataframe.profile import MeterProfileHandler
from pytariff.core.typing import MetricType

from pytariff.core.interval import TariffInterval
from pytariff.core.tariff import GenericTariff


class SingleRateTariff(GenericTariff, Generic[MetricType]):
    """A SingleRateTariff is a subclass of a :ref:`generic_tariff`, with the added restrictions:

    * It must contain at least one, and no more than two, child :ref:`tariff_interval`
    * Each child interval must contain at most one :ref:`tariff_block`, which must be defined with ``from_quantity = 0``
      and ``to_quantity = float("inf")``
    * If two :ref:`tariff_interval` are given, their :ref:`tariff_charge` must be defined on opposite
      :ref:`trade_direction` (``TradeDirection.Import`` and ``TradeDirection.Export``).
    """

    children: tuple[TariffInterval[MetricType], ...]
    """See :ref:`tariff_interval`"""

    @model_validator(mode="after")
    def validate_single_rate_tariff(self) -> "SingleRateTariff":
        """Assert that the ``SingleRateTariff`` instance abides by the conditions listed above."""

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

    def apply_to(self, profile_handler: MeterProfileHandler) -> pd.DataFrame:
        return super().apply_to(profile_handler)
