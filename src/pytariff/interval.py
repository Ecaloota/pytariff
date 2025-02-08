from __future__ import annotations

from dataclasses import dataclass, field

from whenever import Time
from whenever_time_period import AbstractTimePeriod, InfiniteTimePeriod

from pytariff.block import TariffBlock
from pytariff.day import DayType
from pytariff.rate import TariffRate
from pytariff.reset import ResetPeriod
from pytariff.unit import Metric, SignConvention, TradeDirection
from pytariff.utils import (
    intersection_search_sorted_sequence,
    two_pointer_intersection_search,
)

DEFAULT_TIME_PERIOD = InfiniteTimePeriod(
    start_time=Time.MIDNIGHT, end_time=Time.MIDNIGHT
)
DEFAULT_DAYS_APPLIED = set([DayType.ALL_DAYS])


@dataclass
class TariffInterval:
    time_period: AbstractTimePeriod = field(default_factory=lambda: DEFAULT_TIME_PERIOD)
    days_applied: set[DayType] = field(default_factory=lambda: DEFAULT_DAYS_APPLIED)
    blocks: list[TariffBlock] = field(default_factory=list)
    rates: list[TariffRate] = field(default_factory=list)
    reset_period: ResetPeriod | None = None
    trade_direction: TradeDirection = TradeDirection.Import
    sign_convention: SignConvention = SignConvention.Passive
    metric: Metric = Metric.Consumption

    def __post_init__(self) -> None:
        if len(self.blocks) < 1:
            raise ValueError("TariffIntervals must contain at least one TariffBlock")

        if len(self.rates) < 1:
            raise ValueError("TariffIntervals must contain at least one TariffRate")

        if len(self.blocks) != len(self.rates):
            raise ValueError(
                "TariffIntervals must contain equal numbers of TariffBlocks and TariffRates"
            )

        self.br_zip = sorted(zip(self.blocks, self.rates), key=lambda x: x[0])
        sorted_blocks = [t[0] for t in self.br_zip]
        if intersection_search_sorted_sequence(sorted_blocks):
            raise ValueError("TariffIntervals cannot contain intersecting TariffBlocks")

    def _units_equal(self, other: TariffInterval) -> bool:
        return (
            self.trade_direction == other.trade_direction
            and self.sign_convention == other.sign_convention
            and self.metric == other.metric
        )

    # this is an arbitrary choice
    def __lt__(self, other: TariffInterval) -> bool:
        return self.time_period.start_time < other.time_period.start_time

    def __and__(self, other: TariffInterval) -> TariffInterval | None:
        """The intersection between two TariffIntervals is defined to be non-None
        iff each of trade_direction, sign_convention, and metric attributes are exactly equal
        AND each of the intersections between their child time_period, days_applied, and
        blocks list are non-None."""

        if not self._units_equal(other):
            return None

        # block intersection
        block_inter = two_pointer_intersection_search(self.blocks, other.blocks)
        if len(block_inter) < 1:
            return None

        # time period intersection
        time_inter = self.time_period & other.time_period
        if not time_inter:
            return None

        # days intersection
        days_inter = self.days_applied & other.days_applied
        if not days_inter:
            return None

        # rates from an intersection have no semantic meaning, but a
        # rate must always be defined for a given TariffInterval
        rates_inter = [
            TariffRate(currency=None, value=0.0) for _ in range(len(block_inter))
        ]

        return TariffInterval(
            time_period=time_inter,
            days_applied=days_inter,
            blocks=block_inter,
            rates=rates_inter,
            trade_direction=self.trade_direction,
            sign_convention=self.sign_convention,
            metric=self.metric,
        )
