from abc import ABC
from typing import Generic, Optional
from uuid import uuid4

from pydantic import UUID4, model_validator
from pydantic.dataclasses import dataclass


from utal._internal.block import ConsumptionBlock, DemandBlock, TariffBlock
from utal._internal.generic_types import Consumption, Demand, MetricType, TradeDirection
from utal._internal.period import ConsumptionResetPeriod, DemandResetPeriod, ResetPeriod
from utal._internal.unit import ConsumptionUnit, DemandUnit, TariffUnit, UsageChargeMetric


@dataclass
class TariffCharge(ABC, Generic[MetricType]):
    """Not to be used directly"""

    blocks: tuple[TariffBlock, ...]
    unit: TariffUnit[MetricType]
    reset_period: Optional[ResetPeriod]
    method: UsageChargeMetric = UsageChargeMetric.mean
    resolution: str = "5T"  # TODO this should be one of a subset of valid pandas unit strings e.g. 5T
    window: Optional[str] = None  # as above. window is only relevant when method = rolling_mean

    uuid: UUID4 = uuid4()

    @model_validator(mode="after")
    def validate_blocks_cannot_overlap(self) -> "TariffCharge":
        if any([bool(x & y) for i, x in enumerate(self.blocks) for j, y in enumerate(self.blocks) if i != j]):
            raise ValueError
        return self

    @model_validator(mode="after")
    def validate_blocks_are_ordered_by_from_quantity(self) -> "TariffCharge":
        self.blocks = tuple(sorted(self.blocks, key=lambda x: x.from_quantity))
        return self

    @model_validator(mode="after")
    def validate_window_is_non_none_when_method_rolling_mean(self) -> "TariffCharge":
        if self.method == UsageChargeMetric.rolling_mean and self.window is None:
            raise ValueError
        return self

    def __and__(self, other: "TariffCharge[MetricType]") -> "Optional[TariffCharge[MetricType]]":
        """The intersection between two TariffCharges self and other is defined to be the overlap between
        their child blocks iff self.unit == other.unit"""

        # The intersection between two blocks defined in different units is empty
        if self.unit != other.unit:
            return None

        block_overlaps = []
        for block_a in self.blocks:
            for block_b in other.blocks:
                intersection = block_a & block_b
                if intersection is not None:
                    block_overlaps.append(intersection)

        block_tuple = tuple(sorted(block_overlaps, key=lambda x: x.from_quantity))

        # if no overlaps
        if len(block_tuple) < 1:
            return None

        # TODO note this will contain default data such as resolution, which is meaningless in this context
        return TariffCharge(
            blocks=block_tuple,
            unit=self.unit,
            reset_period=None,  # intersection between reset periods is ill-defined
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TariffCharge):
            return False

        return (
            self.blocks == other.blocks
            and self.unit == other.unit
            and self.reset_period == other.reset_period
            and self.method == other.method
            and self.resolution == other.resolution
            and self.window == other.window
        )

    def __hash__(self) -> int:
        # Just some cumbersome XORs
        return (
            hash(self.blocks)
            ^ hash(self.unit)
            ^ hash(self.reset_period)
            ^ hash(self.method)
            ^ hash(self.resolution)
            ^ hash(self.window)
        )


@dataclass
class ConsumptionCharge(TariffCharge[Consumption]):
    blocks: tuple[ConsumptionBlock, ...]
    unit: ConsumptionUnit
    reset_period: Optional[ConsumptionResetPeriod]

    @model_validator(mode="after")
    def validate_blocks_are_consumption_blocks(self) -> "ConsumptionCharge":
        if not all(isinstance(x, ConsumptionBlock) for x in self.blocks):
            raise ValueError
        return self

    def __and__(self, other: "TariffCharge[Consumption]") -> Optional["ConsumptionCharge"]:
        """"""
        # The intersection between two blocks defined in different units is empty
        if self.unit != other.unit:
            return None

        block_overlaps = []
        for block_a in self.blocks:
            for block_b in other.blocks:
                intersection = block_a & block_b
                if intersection is not None:
                    block_overlaps.append(intersection)

        block_tuple = tuple(sorted(block_overlaps, key=lambda x: x.from_quantity))

        # if no overlaps
        if len(block_tuple) < 1:
            return None

        # TODO note this will contain default data such as resolution, which is meaningless in this context
        return ConsumptionCharge(
            blocks=block_tuple,
            unit=self.unit,
            reset_period=None,  # intersection between reset periods is ill-defined
        )


@dataclass
class DemandCharge(TariffCharge[Demand]):
    blocks: tuple[DemandBlock, ...]
    unit: DemandUnit
    reset_period: Optional[DemandResetPeriod]

    @model_validator(mode="after")
    def validate_blocks_are_demand_blocks(self) -> "DemandCharge":
        if not all(isinstance(x, DemandBlock) for x in self.blocks):
            raise ValueError
        return self

    def __and__(self, other: "TariffCharge[Demand]") -> Optional["DemandCharge"]:
        # The intersection between two blocks defined in different units is empty
        if self.unit != other.unit:
            return None

        block_overlaps = []
        for block_a in self.blocks:
            for block_b in other.blocks:
                intersection = block_a & block_b
                if intersection is not None:
                    block_overlaps.append(intersection)

        block_tuple = tuple(sorted(block_overlaps, key=lambda x: x.from_quantity))

        # if no overlaps
        if len(block_tuple) < 1:
            return None

        # TODO note this will contain default data such as resolution, which is meaningless in this context
        return DemandCharge(
            blocks=block_tuple,
            unit=self.unit,
            reset_period=None,  # intersection between reset periods is ill-defined
        )


@dataclass
class ImportConsumptionCharge(ConsumptionCharge):
    unit: ConsumptionUnit

    @model_validator(mode="after")
    def validate_unit_has_import_direction(self) -> "ImportConsumptionCharge":
        if not self.unit.direction == TradeDirection.Import:
            raise ValueError
        return self


@dataclass
class ExportConsumptionCharge(ConsumptionCharge):
    unit: ConsumptionUnit

    @model_validator(mode="after")
    def validate_unit_has_export_direction(self) -> "ExportConsumptionCharge":
        if not self.unit.direction == TradeDirection.Export:
            raise ValueError
        return self
