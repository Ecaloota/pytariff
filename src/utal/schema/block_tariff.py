from datetime import datetime
from pydantic import model_validator
import pandera as pa
from pandera.typing import DataFrame
from utal._internal.generic_types import MetricType
from utal._internal.meter_profile import MeterProfileSchema, TariffCostSchema
from utal._internal.tariff_interval import TariffInterval
from utal.schema.generic_tariff import GenericTariff


class BlockTariff(GenericTariff[MetricType]):
    """A BlockTariff is a subclass of a GenericTariff that enforces that, among other things:
        1. At least one child TariffInterval must be defined
        2. The child TariffInterval(s) must each contain more than a single non-overlapping block

    There are no restrictions on the units of the child TariffIntervals or the existence of reset periods."""

    children: tuple[TariffInterval[MetricType], ...]

    @model_validator(mode="after")
    def validate_block_tariff(self) -> "BlockTariff":
        if len(self.children) < 1:
            raise ValueError

        for child in self.children:
            if len(child.charge.blocks) < 2:
                raise ValueError

        return self

    @pa.check_types
    def apply(
        self, meter_profile: DataFrame[MeterProfileSchema], billing_start: datetime | None
    ) -> DataFrame[TariffCostSchema]:
        return super().apply(meter_profile, billing_start)
