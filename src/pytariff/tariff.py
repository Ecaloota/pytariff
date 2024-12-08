from __future__ import annotations

from dataclasses import dataclass

from pytariff.defined_interval import DefinedInterval
from pytariff.interval import TariffInterval


@dataclass
class TariffComponent(DefinedInterval):
    """A TariffComponent is a generalised model of an electrical tariff defined
    as a closed timezone-aware ZonedDateTime interval. It contains child
    TariffIntervals.
    """

    children: list[TariffInterval]
    # reset_period: ResetPeriod # ? Should this go here or in TariffInterval?

    def __post_init__(self) -> None:
        # children cannot overlap at instantiation
        raise NotImplementedError

    def __and__(self, other: TariffComponent) -> TariffComponent | None:
        """The intersection between TariffComponents is defined to be the intersections
        between their children, if any, iff the superclass DefinedIntervals
        intersect."""
        raise NotImplementedError


@dataclass
class Tariff:
    children: list[TariffComponent]

    def __post_init__(self) -> None:
        # children cannot overlap at instantiation
        raise NotImplementedError

    def __and__(self, other: Tariff) -> Tariff | None:
        """The intersection between Tariffs is defined to be the intersections between
        their children, if any."""
        raise NotImplementedError
