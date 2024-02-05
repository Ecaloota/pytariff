from pydantic import model_validator
from pytariff.core.dataframe.profile import MeterProfileHandler
from pytariff.core.typing import MetricType
from pytariff.core.interval import TariffInterval
from pytariff.core.unit import TariffUnit
from pytariff.core.tariff import GenericTariff
import pandas as pd


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
                    # Units must match to be considered an intersection
                    if child_a.charge.unit != child_b.charge.unit:
                        continue

                    # Tariff intervals must share days_applied and timezone attrs
                    if not (child_a.days_applied == child_b.days_applied and child_a.tzinfo == child_b.tzinfo):
                        raise ValueError(
                            "Tariff intervals in TimeOfUseTariff must share DaysApplied and tzinfo attributes"
                        )

                    # Tariff intervals must contain unique, non-overlapping [start, end) intervals
                    if child_a.start_time is None or child_a.end_time is None:
                        raise ValueError("TimeOfUseTariff children must contain non-null start and end times")
                    if child_b.start_time is None or child_b.end_time is None:
                        raise ValueError("TimeOfUseTariff children must contain non-null start and end times")

                    start_intersection = max(child_a.start_time, child_b.start_time)
                    end_intersection = min(child_a.end_time, child_b.end_time)
                    if start_intersection < end_intersection:
                        raise ValueError(
                            "Tariff intervals in TimeOfUseTariff must contain unique, non-overlapping time intervals"
                        )  # TODO verify this

        return self

    def apply_to(self, profile_handler: MeterProfileHandler, tariff_unit: TariffUnit) -> pd.DataFrame:
        return super().apply_to(profile_handler, tariff_unit)
