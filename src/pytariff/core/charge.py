from typing import Generic, Optional
from uuid import uuid4

from pydantic import UUID4, BaseModel, PrivateAttr, field_validator, model_validator


from pytariff.core.block import ConsumptionBlock, DemandBlock, TariffBlock
from pytariff.core.typing import Consumption, Demand, MetricType
from pytariff.core.unit import TradeDirection
from pytariff.core.reset import ResetData
from pytariff.core.unit import ConsumptionUnit, DemandUnit, TariffUnit, UsageChargeMethod


class TariffCharge(BaseModel, Generic[MetricType]):
    """A ``TariffCharge`` defines information which is used to determine costs of a tariff incurred by some usage
    profile. Specifically, it defines a tuple of ``blocks`` over the ``unit`` domain which, in turn, define the
    cost of participation in that block. Additional parameters are described below.
    """

    blocks: tuple[TariffBlock, ...]
    """Blocks may not overlap. See :ref:`tariff_block`"""

    unit: TariffUnit[MetricType]
    """See :ref:`tariff_unit`."""

    reset_data: Optional[ResetData]
    """If non-None, defines the frequency with which ``Consumption`` or ``Demand`` usage is reset in a given time
    period, as well as when the reset period first began. See :ref:`reset_data`."""

    method: UsageChargeMethod = UsageChargeMethod.identity
    """Defines the method by which a usage profile must be transformed before the current ``TariffCharge`` may be
    levied against it. Valid options are:

    * ``UsageChargeMethod.identity``: No transformation is applied. Charges are levied against the given profile data
      directly, if all other conditions for being charged are met.
    * ``UsageChargeMethod.mean``: Charges are levied against the average of the given profile data, averaged in each
      reset period interval, if all other conditions for being charged are met.
    * ``UsageChargeMethod.max``: Charges are levied against the maximum of the given profile data, averaged in each
      reset period interval, if all other conditions for being charged are met.
    * ``UsageChargeMethod.rolling_mean``: Charges are levied against the rolling average of the given profile data,
      averaged in each reset period interval, if all other conditions for being charged are met. If selected,
      ``self.window`` cannot be None.
    * ``UsageChargeMethod.cumsum``: Charges are levied against the cumulative sum of the given profile data in each
      reset period interval, if all other conditions for being charged are met.
    """

    # TODO Is the description of `mean` above actually true? Do the UsageChargeMethod definitions depend on reset data?
    # If so, do we enforce that reset data is present for all methods other than identity??

    resolution: str = "5T"
    """Defines the resolution of the current TariffCharge, meaning the frequency with which the charge is levied
    against a usage profile. Defaults to five minutes."""

    window: Optional[str] = None
    """Defines the size of the sliding window used to calculated a rolling mean when
    ``self.method == UsageChargeMethod.rolling_mean``."""

    _uuid: UUID4 = PrivateAttr(default_factory=uuid4)

    @field_validator("blocks")
    @classmethod
    def validate_blocks_cannot_overlap(cls, v: tuple[TariffBlock, ...]) -> tuple[TariffBlock, ...]:
        """Validate that no block in the TariffCharge may overlap (intersect) with any other block in the same
        charge.

        Raises:
            ValueError: If ``block_a & block_b`` is non-None for some pair of unique blocks ``block_a`` and ``block_b``.

        Returns:
            tuple[TariffBlock, ...] in sorted order by ``from_quantity``.
        """
        if any([bool(x & y) for i, x in enumerate(v) for j, y in enumerate(v) if i != j]):
            raise ValueError
        return tuple(sorted(v, key=lambda x: x.from_quantity))

    @model_validator(mode="after")
    def validate_window_is_non_none_when_method_rolling_mean(self) -> "TariffCharge":
        """Validate that if ``self.method`` is ``UsageChargeMethod.rolling_mean``, then ``self.window`` cannot
        be ``None``.

        Raises:
            ValueError: If the above condition is not met.
        """

        if self.method == UsageChargeMethod.rolling_mean and self.window is None:
            raise ValueError
        return self

    def __and__(self, other: "TariffCharge[MetricType]") -> "Optional[TariffCharge[MetricType]]":
        """The intersection between two unique ``TariffCharge`` instances is defined to be the overlap between
        their child blocks, if and only if ``self.unit == other.unit``. The intersection between two blocks defined
        in different units is ``None``, and the intersection between any two ``ResetData`` instances is
        defined to be ``None``.
        """

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
            reset_data=None,  # intersection between reset data is ill-defined
        )

    def __eq__(self, other: object) -> bool:
        """A pair of ``TariffCharges`` are considered equal if and only if each of its public fields are equal."""

        if not isinstance(other, TariffCharge):
            return False

        return (
            self.blocks == other.blocks
            and self.unit == other.unit
            and self.reset_data == other.reset_data
            and self.method == other.method
            and self.resolution == other.resolution
            and self.window == other.window
        )

    def __hash__(self) -> int:
        # Just some cumbersome XORs
        return (
            hash(self.blocks)
            ^ hash(self.unit)
            ^ hash(self.reset_data)
            ^ hash(self.method)
            ^ hash(self.resolution)
            ^ hash(self.window)
        )


class ConsumptionCharge(TariffCharge[Consumption]):
    """A ``ConsumptionCharge`` is a ``TariffCharge`` with the added restriction that each of its child blocks are
    ``ConsumptionBlocks``, and its ``unit`` must be an instance of a ``ConsumptionUnit``.
    """

    blocks: tuple[ConsumptionBlock, ...]
    unit: ConsumptionUnit
    """Must be one of ``[Consumption.kWh, Consumption._null]``."""

    @model_validator(mode="after")
    def validate_blocks_are_consumption_blocks(self) -> "ConsumptionCharge":
        """Validate that each block in ``self.blocks`` is an instance of a ``ConsumptionBlock``.

        Raises:
            ValueError: If the above condition is not met.
        """
        if not all(isinstance(x, ConsumptionBlock) for x in self.blocks):
            raise ValueError
        return self

    def __and__(self, other: "TariffCharge[Consumption]") -> Optional["ConsumptionCharge"]:
        """The intersection between two unique ``ConsumptionCharge`` instances is defined to be the overlap between
        their child blocks, if and only if ``self.unit == other.unit``. The intersection between two blocks defined
        in different units is ``None``, and the intersection between any two ``ResetData`` instances is
        defined to be ``None``.
        """
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
            reset_data=None,  # intersection between reset periods is ill-defined
        )

    def __eq__(self, other: object) -> bool:
        """A pair of ``ConsumptionCharges`` are considered equal if and only if each of its public fields are equal."""

        if not isinstance(other, ConsumptionCharge):
            return False

        return (
            self.blocks == other.blocks
            and self.unit == other.unit
            and self.reset_data == other.reset_data
            and self.method == other.method
            and self.resolution == other.resolution
            and self.window == other.window
        )


class DemandCharge(TariffCharge[Demand]):
    """A ``DemandCharge`` is a ``TariffCharge`` with the added restriction that each of its child blocks are
    ``DemandBlocks``, and its ``unit`` must be an instance of a ``DemandUnit``.
    """

    blocks: tuple[DemandBlock, ...]
    unit: DemandUnit
    """Must be one of [Demand.kW, Demand._null]"""

    @model_validator(mode="after")
    def validate_blocks_are_demand_blocks(self) -> "DemandCharge":
        """Validate that each block in ``self.blocks`` is an instance of a ``DemandBlock``.

        Raises:
            ValueError: If the above condition is not met.
        """

        if not all(isinstance(x, DemandBlock) for x in self.blocks):
            raise ValueError
        return self

    def __and__(self, other: "TariffCharge[Demand]") -> Optional["DemandCharge"]:
        """The intersection between two unique ``DemandCharge`` instances is defined to be the overlap between
        their child blocks, if and only if ``self.unit == other.unit``. The intersection between two blocks defined
        in different units is ``None``, and the intersection between any two ``ResetData`` instances is
        defined to be ``None``.
        """
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
            reset_data=None,  # intersection between reset periods is ill-defined
        )

    def __eq__(self, other: object) -> bool:
        """A pair of ``DemandCharges`` are considered equal if and only if each of its public fields are equal."""
        if not isinstance(other, DemandCharge):
            return False

        return (
            self.blocks == other.blocks
            and self.unit == other.unit
            and self.reset_data == other.reset_data
            and self.method == other.method
            and self.resolution == other.resolution
            and self.window == other.window
        )


class ImportConsumptionCharge(ConsumptionCharge):
    """An ``ImportConsumptionCharge`` is a ``ConsumptionCharge`` with the added restriction that its ``unit.direction``
    is defined to be ``TradeDirection.Import``.
    """

    unit: ConsumptionUnit

    @model_validator(mode="after")
    def validate_unit_has_import_direction(self) -> "ImportConsumptionCharge":
        """Validate that ``unit.direction == TradeDirection.Import``.

        Raises:
            ValueError: If the above condition is not True.
        """
        if not self.unit.direction == TradeDirection.Import:
            raise ValueError
        return self


class ExportConsumptionCharge(ConsumptionCharge):
    """An ``ExportConsumptionCharge`` is a ``ConsumptionCharge`` with the added restriction that its ``unit.direction``
    is defined to be ``TradeDirection.Export``.
    """

    unit: ConsumptionUnit

    @model_validator(mode="after")
    def validate_unit_has_export_direction(self) -> "ExportConsumptionCharge":
        """Validate that ``unit.direction == TradeDirection.Export``.

        Raises:
            ValueError: If the above condition is not True.
        """
        if not self.unit.direction == TradeDirection.Export:
            raise ValueError
        return self
