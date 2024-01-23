from abc import ABC
from typing import Generic, Optional

from pydantic import Field, model_validator
from pydantic.dataclasses import dataclass

from utal._internal.generic_types import Consumption, Demand, MetricType
from utal._internal.rate import TariffRate


@dataclass
class TariffBlock(ABC, Generic[MetricType]):
    """Not to be used directly.

    TariffBlocks are right-open intervals over [from_quantity, to_quantity) defined for some unit
    and associated with a rate.
    """

    rate: Optional[TariffRate[MetricType]]
    from_quantity: float = Field(ge=0)
    to_quantity: float = Field(gt=0)

    @model_validator(mode="after")  # type: ignore
    def assert_from_lt_to(self) -> "TariffBlock":
        if self.to_quantity <= self.from_quantity:
            raise ValueError
        return self

    def __and__(self, other: "TariffBlock[MetricType]") -> "Optional[TariffBlock[MetricType]]":
        """An intersection between two TariffBlocks [a, b) and [c, d) is defined as the
        TariffBlock with [max(a, c), min(b, d)). The intersection between any two TariffRates is
        always None.
        """
        if not isinstance(other, TariffBlock):
            raise ValueError

        from_intersection = max(self.from_quantity, other.from_quantity)
        to_intersection = min(self.to_quantity, other.to_quantity)

        # right-open intersection edge condition, when self.to_quantity == other.from_quantity
        if from_intersection == to_intersection:
            return None

        # # if from < to, no intersection
        if to_intersection < from_intersection:
            return None

        return TariffBlock(
            from_quantity=from_intersection,
            to_quantity=to_intersection,
            rate=None,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TariffBlock):
            raise NotImplementedError
        return (
            self.from_quantity == other.from_quantity
            and self.to_quantity == other.to_quantity
            and self.rate == other.rate
        )


@dataclass
class DemandBlock(TariffBlock[Demand]):
    ...

    def __and__(self, other: "TariffBlock[Demand]") -> "Optional[DemandBlock]":
        generic_block = super().__and__(other)
        if generic_block is None:
            return generic_block
        return DemandBlock(
            from_quantity=generic_block.from_quantity, to_quantity=generic_block.to_quantity, rate=generic_block.rate
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DemandBlock):
            raise NotImplementedError
        return (
            self.from_quantity == other.from_quantity
            and self.to_quantity == other.to_quantity
            and self.rate == other.rate
        )


@dataclass
class ConsumptionBlock(TariffBlock[Consumption]):
    ...

    def __and__(self, other: "TariffBlock[Consumption]") -> Optional["ConsumptionBlock"]:
        generic_block = super().__and__(other)
        if generic_block is None:
            return generic_block
        return ConsumptionBlock(
            from_quantity=generic_block.from_quantity, to_quantity=generic_block.to_quantity, rate=generic_block.rate
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ConsumptionBlock):
            raise NotImplementedError
        return (
            self.from_quantity == other.from_quantity
            and self.to_quantity == other.to_quantity
            and self.rate == other.rate
        )
