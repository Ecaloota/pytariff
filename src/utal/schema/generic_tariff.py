from typing import Generic, Optional

import pandera as pa
from pandera.typing import DataFrame

# from utal.schema.block import ConsumptionBlock, DemandBlock
from utal.schema.defined_interval import DefinedInterval
from utal.schema.generic_types import Consumption, Demand, GenericType
from utal.schema.meter_profile import MeterProfileSchema, TariffCostSchema
from utal.schema.tariff_interval import (
    ConsumptionInterval,
    DemandInterval,
    TariffInterval,
)


class GenericTariff(DefinedInterval, Generic[GenericType]):
    # class GenericTariff(DefinedInterval):
    """A GenericTariff is a closed datetime interval from [start, end]"""

    children: Optional[tuple[TariffInterval, ...]] = None

    @pa.check_types
    def apply(self, meter_profile: DataFrame[MeterProfileSchema]) -> DataFrame[TariffCostSchema]:
        raise NotImplementedError


class ConsumptionTariff(DefinedInterval, Consumption):
    """A ConsumptionTariff is a closed datetime interval from [start, end]"""

    children: Optional[tuple[ConsumptionInterval, ...]] = None

    @pa.check_types
    def apply(self, meter_profile: DataFrame[MeterProfileSchema]) -> DataFrame[TariffCostSchema]:
        raise NotImplementedError


class DemandTariff(DefinedInterval, Demand):
    """A ConsumptionTariff is a closed datetime interval from [start, end]"""

    children: Optional[tuple[DemandInterval, ...]] = None

    @pa.check_types
    def apply(self, meter_profile: DataFrame[MeterProfileSchema]) -> DataFrame[TariffCostSchema]:
        raise NotImplementedError
