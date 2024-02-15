from pydantic import model_validator
from pytariff.core.dataframe.profile import MeterProfileHandler
from pytariff.core.typing import MetricType
from pytariff.core.interval import TariffInterval
from pytariff.core.tariff import GenericTariff
import pandas as pd


class TimeOfUseTariff(GenericTariff[MetricType]):
    """A SingleRateTariff is a subclass of a :ref:`generic_tariff`, with the added restrictions:

    * It must contain more than one unique child :ref:`tariff_interval`
    * Those children must share their :ref:`days_applied` and contain unique, non-overlapping ``[start, end)``
      intervals.

    .. note:: There are no restrictions that prevent each child :ref:`tariff_interval` in the ``TimeOfUseTariff`` from
       containing multiple non-overlapping :ref:`tariff_block`, and no restrictions on the existence of reset periods
       on each :ref:`tariff_interval`.

    .. note:: A ``TimeOfUseTariff`` may be defined in terms of either :ref:`demand` or :ref:`consumption` units,
       but not both.
    """

    children: tuple[TariffInterval[MetricType], ...]

    @model_validator(mode="after")
    def validate_time_of_use_tariff(self) -> "TimeOfUseTariff":
        """Asserts that the current instance abides by the restrictions listed above."""

        if len(self.children) < 2 or len(set(self.children)) < 2:
            raise ValueError

        for i, child_a in enumerate(self.children):
            for j, child_b in enumerate(self.children):
                if i != j:
                    # Units must match to be considered an intersection
                    if child_a.charge.unit != child_b.charge.unit:
                        continue

                    # Tariff intervals must share days_applied
                    if not (child_a.days_applied == child_b.days_applied):
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

    def apply_to(self, profile_handler: MeterProfileHandler) -> pd.DataFrame:
        return super().apply_to(profile_handler)
