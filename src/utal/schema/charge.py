from typing import Generic, TypeVar

from pydantic import model_validator
from pydantic.dataclasses import dataclass

from utal.schema.block import ConsumptionBlock, DemandBlock

T = TypeVar("T", ConsumptionBlock, DemandBlock)


@dataclass
class TariffCharge(Generic[T]):
    """Not to be used directly"""

    blocks: tuple[T, ...]

    @model_validator(mode="after")
    def validate_blocks_cannot_overlap(self) -> "TariffCharge":
        if any([bool(x & y) for i, x in enumerate(self.blocks) for j, y in enumerate(self.blocks) if i != j]):
            raise ValueError
        return self


@dataclass
class ConsumptionCharge(TariffCharge[ConsumptionBlock]):
    pass


@dataclass
class DemandCharge(TariffCharge[DemandBlock]):
    pass
