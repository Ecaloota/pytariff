from abc import ABC
from typing import Generic, Optional

from pydantic import Field, model_validator
from pydantic.dataclasses import dataclass

from utal.schema.generic_types import Consumption, Demand, Export, GenericType, Import, LevyType
from utal.schema.rate import TariffRate
from utal.schema.unit import ConsumptionUnit, DemandUnit, TariffUnit


@dataclass
class TariffBlock(ABC, Generic[GenericType]):
    """Not to be used directly.

    TariffBlocks are right-open intervals over [from_quantity, to_quantity) defined for some unit
    and associated with a rate.
    """

    unit: Optional[TariffUnit]
    rate: Optional[TariffRate[GenericType]]
    from_quantity: float = Field(ge=0)
    to_quantity: float = Field(gt=0)

    @model_validator(mode="after")  # type: ignore
    def assert_from_lt_to(self) -> "TariffBlock":
        if self.to_quantity <= self.from_quantity:
            raise ValueError
        return self

    def __and__(self, other: GenericType) -> GenericType:
        raise NotImplementedError


class DemandBlock(TariffBlock, Demand, Generic[LevyType]):
    unit: Optional[DemandUnit]

    def __and__(self, other: "DemandBlock") -> "DemandBlock":
        """TODO"""
        raise NotImplementedError


class ConsumptionBlock(TariffBlock, Consumption, Generic[LevyType]):
    unit: Optional[ConsumptionUnit]

    def __and__(self, other: "ConsumptionBlock") -> Optional["ConsumptionBlock"]:
        """An intersection between two ConsumptionBlocks [a, b) and [c, d) is defined as the
        ConsumptionBlock with [max(a, c), min(b, d)) iff self.unit == other.unit.

        The intersection between any two TariffRates is always None.
        """

        if not isinstance(other, ConsumptionBlock):
            raise ValueError

        # The intersection between two blocks defined in different units is empty
        if self.unit != other.unit:
            return None

        from_intersection = max(self.from_quantity, other.from_quantity)
        to_intersection = min(self.to_quantity, other.to_quantity)

        # right-open intersection edge condition, when self.to_quantity == other.from_quantity
        if from_intersection == to_intersection:
            return None

        return ConsumptionBlock(
            from_quantity=from_intersection,
            to_quantity=to_intersection,
            unit=self.unit,
            rate=None,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ConsumptionBlock):
            raise NotImplementedError
        return self.from_quantity == other.from_quantity and self.unit == other.unit and self.rate == other.rate

    def quantities_and_types_equal(self, other: object) -> bool:
        """Weaker assertion of equality between ConsumptionBlocks which does not depend on rate
        equality, as the intersection between two rates is always None"""
        if not isinstance(other, ConsumptionBlock):
            raise NotImplementedError
        return self.from_quantity == other.from_quantity and self.unit == other.unit


class ImportConsumptionBlock(ConsumptionBlock, Import):
    pass


class ExportConsumptionBlock(ConsumptionBlock, Export):
    pass
