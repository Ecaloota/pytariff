from abc import ABC
from typing import Generic, Optional

from pydantic import model_validator
from pydantic.dataclasses import dataclass

from utal.schema.block import ConsumptionBlock, DemandBlock, TariffBlock
from utal.schema.generic_types import Consumption, Demand, MetricType
from utal.schema.period import ConsumptionResetPeriod, DemandResetPeriod, ResetPeriod
from utal.schema.unit import ConsumptionUnit, DemandUnit, TariffUnit


@dataclass
class TariffCharge(ABC, Generic[MetricType]):
    """Not to be used directly"""

    blocks: tuple[TariffBlock[MetricType], ...]
    unit: Optional[TariffUnit[MetricType]]
    reset_period: Optional[ResetPeriod]

    @model_validator(mode="after")
    def validate_blocks_cannot_overlap(self) -> "TariffCharge":
        if any([bool(x & y) for i, x in enumerate(self.blocks) for j, y in enumerate(self.blocks) if i != j]):
            raise ValueError
        return self


@dataclass
class ConsumptionCharge(TariffCharge[Consumption]):
    blocks: tuple[ConsumptionBlock, ...]
    unit: Optional[ConsumptionUnit]
    reset_period: Optional[ConsumptionResetPeriod]

    @model_validator(mode="after")
    def validate_blocks_are_consumption_blocks(self) -> "ConsumptionCharge":
        if not all(isinstance(x, ConsumptionBlock) for x in self.blocks):
            raise ValueError
        return self

    # TODO validate unit is consumption unit


@dataclass
class DemandCharge(TariffCharge[Demand]):
    blocks: tuple[DemandBlock, ...]
    unit: Optional[DemandUnit]
    reset_period: DemandResetPeriod

    @model_validator(mode="after")
    def validate_blocks_are_demand_blocks(self) -> "DemandCharge":
        if not all(isinstance(x, DemandBlock) for x in self.blocks):
            raise ValueError
        return self

    # TODO validate unit is demand unit


# TODO create import and export versions of above consumption and demand charges?
# difference is just the addition of validation of unit.direction
