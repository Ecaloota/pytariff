from __future__ import annotations

from dataclasses import dataclass

from pytariff.defined_interval import DefinedInterval
from pytariff.interval import TariffInterval
from pytariff.utils import (
    intersection_search_sorted_sequence,
    two_pointer_intersection_search,
)


@dataclass
class TariffComponent(DefinedInterval):
    """A TariffComponent is a generalised model of an electrical tariff defined
    as a closed timezone-aware ZonedDateTime interval. It contains child
    TariffIntervals.
    """

    children: list[TariffInterval]

    def __post_init__(self) -> None:
        self.children = sorted(self.children)
        if intersection_search_sorted_sequence(self.children):
            raise ValueError(
                "TariffComponents cannot contain intersecting TariffIntervals"
            )

    def __and__(self, other: TariffComponent) -> TariffComponent | None:
        """The intersection between TariffComponents is defined to be the intersections
        between their children, if any, iff the superclass DefinedIntervals
        intersect."""

        dt_inter = super().__and__(other)

        if not dt_inter:
            return None

        child_inter = two_pointer_intersection_search(self.children, other.children)
        if len(child_inter) < 1:
            return None

        return TariffComponent(
            start=dt_inter.start, end=dt_inter.end, children=child_inter
        )

    def __lt__(self, other: TariffComponent) -> bool:
        return self.start < other.start


@dataclass
class Tariff:
    children: list[TariffComponent]

    def __post_init__(self) -> None:
        self.children = sorted(self.children)
        if intersection_search_sorted_sequence(self.children):
            raise ValueError("Tariffs cannot contain intersecting TariffComponents")

    def __and__(self, other: Tariff) -> Tariff | None:
        """The intersection between Tariffs is defined to be the intersections between
        their children, if any."""

        child_inter = two_pointer_intersection_search(self.children, other.children)
        if len(child_inter) < 1:
            return None

        return Tariff(children=child_inter)
