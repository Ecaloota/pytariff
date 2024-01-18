from abc import ABC
from typing import Generic

from pydantic.dataclasses import dataclass

from utal.schema.generic_types import Consumption, Demand, MetricType
from utal.schema.unit import RateCurrency


@dataclass
class TariffRate(ABC, Generic[MetricType]):
    """A rate is a value in some registered currency. It has no meaning independent of a parent
    TariffBlock.unit

    Not to be used directly
    """

    currency: RateCurrency
    value: float


@dataclass
class DemandTariffRate(TariffRate[Demand]):
    """A DemandTariffRate is a TariffRate that accepts information about
    a reset_period.

    A demand charge is calculated as the peak demand (in the peak period)
    over some reset period, e.g. 5 kW on 11th day of month between
    9am - 3pm, multiplied by the length of the reset period.
    """

    pass
    # reset_period: DemandResetPeriod


@dataclass
class ConsumptionTariffRate(TariffRate[Consumption]):
    """A ConsumptionTariffRate is a TariffRate that accepts information about
    a consumption reset period.
    """

    pass
    # reset_period: ConsumptionResetPeriod
