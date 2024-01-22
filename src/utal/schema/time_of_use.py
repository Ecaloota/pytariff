from datetime import datetime
from pydantic import model_validator
from utal._internal.generic_types import MetricType
from utal._internal.meter_profile import MeterProfileSchema, TariffCostSchema
from utal._internal.tariff_interval import TariffInterval
from utal.schema.generic_tariff import GenericTariff
import pandera as pa
from pandera.typing import DataFrame


class TimeOfUseTariff(GenericTariff[MetricType]):
    """A TimeOfUseTariff is a subclass of a GenericTariff that enforces that, among other things:
        1. More than one unique child TariffInterval must be defined
        2. These TariffIntervals must share their DaysApplied and timezone attributes, and contain unique,
            non-overlapping [start, end) intervals

    There are no restrictions preventing each child TariffInterval in the TimeOfUseTariff from containing multiple
    non-overlapping blocks, and no restriction on the existence of reset periods on each TariffInterval. A
    TimeOfUseTariff can be defined in terms of either Demand or Consumption units (but not both).
    """

    children: tuple[TariffInterval[MetricType], ...]

    @model_validator(mode="after")
    def validate_time_of_use_tariff(self) -> "TimeOfUseTariff":
        # TODO
        return self

    @pa.check_types
    def apply(
        self, meter_profile: DataFrame[MeterProfileSchema], billing_start: datetime | None
    ) -> DataFrame[TariffCostSchema]:
        return super().apply(meter_profile, billing_start)
