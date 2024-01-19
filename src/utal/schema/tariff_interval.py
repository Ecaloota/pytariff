from typing import Generic

from pydantic import model_validator

from utal.schema.applied_interval import AppliedInterval
from utal.schema.charge import ConsumptionCharge, DemandCharge, TariffCharge
from utal.schema.generic_types import Consumption, Demand, MetricType


class TariffInterval(AppliedInterval, Generic[MetricType]):
    """A TariffInterval is a right-open time interval over [start_time, end_time)
    associated with a single TariffCharge"""

    charge: TariffCharge[MetricType]


class ConsumptionInterval(TariffInterval[Consumption]):
    charge: ConsumptionCharge

    @model_validator(mode="after")
    def validate_charges_are_consumption_charges(self) -> "ConsumptionInterval":
        if not isinstance(self.charge, ConsumptionCharge):
            raise ValueError
        return self


class DemandInterval(TariffInterval[Demand]):
    charge: DemandCharge

    @model_validator(mode="after")
    def validate_charges_are_demand_charges(self) -> "DemandInterval":
        if not isinstance(self.charge, DemandCharge):
            raise ValueError
        return self
