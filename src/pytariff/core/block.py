from typing import Optional
from uuid import uuid4

from pydantic import UUID4, BaseModel, Field, PrivateAttr, model_validator

from pytariff.core.rate import MarketRate, TariffRate


class TariffBlock(BaseModel):
    """
    ``TariffBlocks`` are right-open intervals over ``[from_quantity, to_quantity)`` associated with a
    ``TariffRate`` or ``MarketRate``.
    """

    rate: Optional[TariffRate | MarketRate]
    """See :ref:`class`"""

    from_quantity: float = Field(ge=0)
    """The minimum quantity from which the ``TarriffBlock`` is levied (inclusive). Must be greater than zero units.
    Cannot be greater than or equal to ``to_quantity``."""

    to_quantity: float = Field(gt=0)
    """The minimum quantity from which the ``TarriffBlock`` is levied (exclusive). Must be greater than zero units.
    Cannot be less than or equal to ``from_quantity``."""

    _uuid: UUID4 = PrivateAttr(default_factory=uuid4)

    @model_validator(mode="after")
    def assert_from_lt_to(self) -> "TariffBlock":
        """Validate that ``self.from_quantity`` be strictly greater than ``self.to_quantity``.

        Raises:
            ValueError: If ``self.to_quantity <= self.from_quantity``
        """

        if self.to_quantity <= self.from_quantity:
            raise ValueError
        return self

    def __and__(self, other: "TariffBlock") -> "Optional[TariffBlock]":
        """An intersection between two TariffBlocks [a, b) and [c, d) is defined as the
        ``TariffBlock`` with ``from_quantity = max(a, c)`` and ``to_quantity = min(b, d)``.
        The intersection between any two ``TariffRates`` is always ``None``."""
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
        """A pair of ``TariffBlocks`` are considered equal if and only if each of ``from_quantity``, ``to_quantity``,
        and ``rate`` are equal.

        Raises:
            NotImplementedError: If ``other`` is not a ``TariffBlock`` instance.
        """

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
        """A ``TariffBlock`` contains a given float ``other`` if and only if
        ``self.from_quantity <= other < self.to_quantity``"""

        # TODO test the equality condition on to_quantity
        return self.from_quantity <= other < self.to_quantity


class DemandBlock(TariffBlock):
    ...

    def __and__(self, other: "TariffBlock") -> "Optional[DemandBlock]":
        """An intersection between two DemandBlocks [a, b) and [c, d) is defined as the
        ``DemandBlock`` with ``from_quantity = max(a, c)`` and ``to_quantity = min(b, d)``.
        The intersection between any two ``TariffRates`` is always ``None``."""

        generic_block = super().__and__(other)
        if generic_block is None:
            return generic_block
        return DemandBlock(
            from_quantity=generic_block.from_quantity, to_quantity=generic_block.to_quantity, rate=generic_block.rate
        )

    def __eq__(self, other: object) -> bool:
        """A pair of ``DemandBlocks`` are considered equal if and only if each of ``from_quantity``, ``to_quantity``,
        and ``rate`` are equal.

        Raises:
            NotImplementedError: If ``other`` is not a ``DemandBlock`` instance.
        """

        if not isinstance(other, DemandBlock):
            raise NotImplementedError
        return (
            self.from_quantity == other.from_quantity
            and self.to_quantity == other.to_quantity
            and self.rate == other.rate
        )

    def __hash__(self) -> int:
        return super().__hash__()


class ConsumptionBlock(TariffBlock):
    ...

    def __and__(self, other: "TariffBlock") -> Optional["ConsumptionBlock"]:
        """An intersection between two ConsumptionBlocks [a, b) and [c, d) is defined as the
        ``ConsumptionBlock`` with ``from_quantity = max(a, c)`` and ``to_quantity = min(b, d)``.
        The intersection between any two ``TariffRates`` is always ``None``."""

        generic_block = super().__and__(other)
        if generic_block is None:
            return generic_block
        return ConsumptionBlock(
            from_quantity=generic_block.from_quantity, to_quantity=generic_block.to_quantity, rate=generic_block.rate
        )

    def __eq__(self, other: object) -> bool:
        """A pair of ``ConsumptionBlocks`` are considered equal if and only if each of ``from_quantity``,
        ``to_quantity``, and ``rate`` are equal.

        Raises:
            NotImplementedError: If ``other`` is not a ``ConsumptionBlock`` instance.
        """

        if not isinstance(other, ConsumptionBlock):
            raise NotImplementedError
        return (
            self.from_quantity == other.from_quantity
            and self.to_quantity == other.to_quantity
            and self.rate == other.rate
        )

    def __hash__(self) -> int:
        return super().__hash__()
