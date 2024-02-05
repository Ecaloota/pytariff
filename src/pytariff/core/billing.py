from datetime import datetime
from enum import Enum
from pydantic.dataclasses import dataclass


class BillingPeriod(Enum):
    DAILY = "1D"
    WEEKLY = "7D"
    FIRST_OF_MONTH = "_null_first_of_month"
    FIRST_OF_QUARTER = "_null_first_of_quarter"

    def _is_day_suffix(self) -> bool:
        return self.name in ["DAILY", "WEEKLY", "FIRST_OF_MONTH", "FIRST_OF_QUARTER"]

    def _to_days(self, _from: datetime) -> str:
        """Convert the ResetPeriod to some number of days, required when using reset periods of
        MONTHLY, QUARTERLY, ANNUALLY. Dates are exclusive.

        NOTE same as ResetPeriod method of same name, TODO consolidate
        """

        if self.name == "FIRST_OF_MONTH":
            next_first_of_month = _from.replace(month=_from.month + 1, day=1)
            return str((next_first_of_month - _from).days) + "D"

        elif self.name == "FIRST_OF_QUARTER":
            # next quarter occurs in one of Jan, Apr, Jul, or Oct
            next_first_of_quarter = _from.replace(month=(_from.month - 1) // 3 * 3 + 4, day=1)
            return str((next_first_of_quarter - _from).days) + "D"

        # add more logic here for more BillingPeriods

        else:
            return self.value


@dataclass
class BillingData:
    start: datetime
    frequency: BillingPeriod = BillingPeriod.FIRST_OF_MONTH  # default 1/month
