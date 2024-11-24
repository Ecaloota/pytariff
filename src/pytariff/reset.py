from datetime import datetime, timedelta
from enum import Enum

from pydantic.dataclasses import dataclass
from pydantic import model_validator
from pytariff._internal.helper import is_aware


class ResetPeriod(Enum):
    QUARTER_HOURLY = "15min"
    HALF_HOURLY = "30min"
    HOURLY = "1h"
    DAILY = "1D"
    WEEKLY = "7D"
    FIRST_OF_MONTH = "_null_first_of_month"
    FIRST_OF_QUARTER = "_null_first_of_quarter"

    def _is_minutely(self) -> bool:
        return self.name in ["QUARTER_HOURLY", "HALF_HOURLY"]

    def _is_hourly(self) -> bool:
        return self.name in ["HOURLY"]

    def _is_daily(self) -> bool:
        return self.name in ["DAILY", "WEEKLY"]

    def count_occurences(self, until: datetime, reference: datetime) -> int:
        """Count the number of times since reference time until time until that the given ResetPeriod
        has occurred. Used to keep track of ResetPeriods"""

        # TODO handling of delta and day_replace is very ugly

        current = reference
        count = 0
        day_replace = False

        if self._is_minutely():
            delta = timedelta(minutes=int(self.value.replace("min", "")))

        elif self._is_hourly():
            delta = timedelta(hours=int(self.value.replace("h", "")))

        elif self._is_daily():
            delta = timedelta(days=int(self.value.replace("D", "")))

        elif self.name == "FIRST_OF_MONTH":
            delta = timedelta(days=32)  # always longer than longest month => after day_replace, will count months
            day_replace = True

        elif self.name == "FIRST_OF_QUARTER":
            delta = timedelta(days=93)  # always longer than longest quarter => after day_replace, will count quarters
            day_replace = True

        while current <= until:
            count += 1

            if day_replace:
                current = (current + delta).replace(day=1)
            else:
                current = current + delta

        return count


@dataclass
class ResetData:
    """Contains information about when the reset period anchor (start), and the frequency with
    which it is reset"""

    anchor: datetime
    period: ResetPeriod

    @model_validator(mode="after")
    def assert_anchor_tz_aware(self) -> "ResetData":
        if not is_aware(self.anchor):
            raise ValueError("ResetData anchor cannot be naive")
        return self

    def __hash__(self) -> int:
        return hash(self.anchor) ^ hash(self.period)
