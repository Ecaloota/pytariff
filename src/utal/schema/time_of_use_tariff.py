from pydantic import model_validator
from utal._internal.generic_types import MetricType
from utal._internal.meter_profile import MeterProfileSchema, TariffCostSchema
from utal._internal.tariff_interval import TariffInterval
from utal._internal.unit import TariffUnit
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
        if len(self.children) < 2 or len(set(self.children)) < 2:
            raise ValueError

        for i, child_a in enumerate(self.children):
            for j, child_b in enumerate(self.children):
                if i != j:
                    # Tariff intervals must share days_applied and timezone attrs
                    if not (child_a.days_applied == child_b.days_applied and child_a.tzinfo == child_b.tzinfo):
                        raise ValueError

                    # Tariff intervals must contain unique, non-overlapping [start, end) intervals
                    if child_a.start_time is None or child_a.end_time is None:
                        raise ValueError
                    if child_b.start_time is None or child_b.end_time is None:
                        raise ValueError

                    start_intersection = max(child_a.start_time, child_b.start_time)
                    end_intersection = min(child_a.end_time, child_b.end_time)
                    if start_intersection < end_intersection:
                        raise ValueError  # TODO verify this

        return self

    @pa.check_types
    def apply(
        self, meter_profile: DataFrame[MeterProfileSchema], tariff_unit: TariffUnit
    ) -> DataFrame[TariffCostSchema]:
        return super().apply(meter_profile, tariff_unit)
