from __future__ import annotations

from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class TariffBlock:
    """
    TariffBlocks are immutable right-open intervals over positive reals (union infinity)
    [from_quantity, to_quantity) defined for some unit and associated with a rate.
    """

    from_quantity: float
    to_quantity: float

    def __post_init__(self) -> None:
        if self.from_quantity >= self.to_quantity:
            raise ValueError

        if self.from_quantity < 0 or self.to_quantity < 0:
            raise ValueError

    def __and__(self, other: TariffBlock) -> TariffBlock | None:
        """TODO"""

        from_intersection = max(self.from_quantity, other.from_quantity)
        to_intersection = min(self.to_quantity, other.to_quantity)

        if from_intersection >= to_intersection:
            return None

        return TariffBlock(
            from_quantity=from_intersection,
            to_quantity=to_intersection,
        )

    def __lt__(self, other: TariffBlock) -> bool:
        return self.from_quantity < other.from_quantity
