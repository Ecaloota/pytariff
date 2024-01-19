from abc import ABC
from typing import Generic

from pydantic import model_validator
from pydantic.dataclasses import dataclass

from utal.schema.block import ConsumptionBlock, DemandBlock, TariffBlock
from utal.schema.generic_types import Consumption, Demand, MetricType


@dataclass
class TariffCharge(ABC, Generic[MetricType]):
    """Not to be used directly"""

    blocks: tuple[TariffBlock[MetricType], ...]

    @model_validator(mode="after")
    def validate_blocks_cannot_overlap(self) -> "TariffCharge":
        if any([bool(x & y) for i, x in enumerate(self.blocks) for j, y in enumerate(self.blocks) if i != j]):
            raise ValueError
        return self


@dataclass
class ConsumptionCharge(TariffCharge[Consumption]):
    blocks: tuple[ConsumptionBlock, ...]

    @model_validator(mode="after")
    def validate_blocks_are_consumption_blocks(self) -> "ConsumptionCharge":
        if not all(isinstance(x, ConsumptionBlock) for x in self.blocks):
            raise ValueError
        return self


@dataclass
class DemandCharge(TariffCharge[Demand]):
    blocks: tuple[DemandBlock, ...]

    @model_validator(mode="after")
    def validate_blocks_are_demand_blocks(self) -> "DemandCharge":
        if not all(isinstance(x, DemandBlock) for x in self.blocks):
            raise ValueError
        return self
