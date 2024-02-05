from typing import Optional
from uuid import uuid4

from pydantic import UUID4, Field, model_validator
from pydantic.dataclasses import dataclass

from pytariff.core.rate import MarketRate, TariffRate


@dataclass
class TariffBlock:
    """
    TariffBlocks are right-open intervals over [from_quantity, to_quantity) defined for some unit
    and associated with a rate.
    """

    rate: Optional[TariffRate | MarketRate]
    from_quantity: float = Field(ge=0)
    to_quantity: float = Field(gt=0)

    uuid: UUID4 = Field(default_factory=uuid4)

    @model_validator(mode="after")
    def assert_from_lt_to(self) -> "TariffBlock":
        if self.to_quantity <= self.from_quantity:
            raise ValueError
        return self

    def __and__(self, other: "TariffBlock") -> "Optional[TariffBlock]":
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

    def __hash__(self) -> int:
        return hash(self.rate) ^ hash(self.from_quantity) ^ hash(self.to_quantity)

    def __contains__(self, other: float) -> bool:
        # TODO test the equality condition on to_quantity
        return self.from_quantity <= other < self.to_quantity


@dataclass
class DemandBlock(TariffBlock):
    ...

    def __and__(self, other: "TariffBlock") -> "Optional[DemandBlock]":
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

    def __hash__(self) -> int:
        return super().__hash__()


@dataclass
class ConsumptionBlock(TariffBlock):
    ...

    def __and__(self, other: "TariffBlock") -> Optional["ConsumptionBlock"]:
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

    def __hash__(self) -> int:
        return super().__hash__()
