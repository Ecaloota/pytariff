from datetime import date, datetime, time
from typing import Generic, Optional
from uuid import uuid4

from pydantic import UUID4, Field, model_validator

from pytariff._internal.applied_interval import AppliedInterval
from pytariff.core.charge import ConsumptionCharge, DemandCharge, TariffCharge
from pytariff.core.typing import Consumption, Demand, MetricType


class TariffInterval(AppliedInterval, Generic[MetricType]):
    """A TariffInterval is a right-open time interval over [start_time, end_time)
    associated with a single TariffCharge"""

    charge: TariffCharge[MetricType]
    uuid: UUID4 = Field(default_factory=uuid4)

    # TODO resolve the type error in line below
    def __and__(self, other: "TariffInterval") -> Optional["TariffInterval"]:  # type: ignore
        """The intersection between two TariffIntervals is the superclass intersection and
        the intersection between self.charge and other.charge

        If the superclass intersection is None, there can be no intersection between the TariffIntervals.
        Likewise, if there is no charge intersection, there is no intersection between the TariffIntervals.
        """

        super_intersection = super().__and__(other)
        if super_intersection is None:
            return super_intersection

        charge_intersection = self.charge & other.charge
        if charge_intersection is None:
            return charge_intersection

        return TariffInterval(
            start_time=super_intersection.start_time,
            end_time=super_intersection.end_time,
            days_applied=super_intersection.days_applied,
            tzinfo=super_intersection.tzinfo,
            charge=charge_intersection,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TariffInterval):
            return False
        return super().__eq__(other) and self.charge == other.charge

    def __hash__(self) -> int:
        return super().__hash__() ^ hash(self.charge)

    def __contains__(self, other: time | date | datetime) -> bool:
        return super().__contains__(other)


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
