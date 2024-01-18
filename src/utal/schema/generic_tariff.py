from typing import Generic, Optional

import pandera as pa
from pandera.typing import DataFrame
from utal.schema.block import ImportConsumptionBlock
from utal.schema.defined_interval import DefinedInterval
from utal.schema.generic_types import Consumption, Demand, MetricType
from utal.schema.meter_profile import MeterProfileSchema, TariffCostSchema, resample
from utal.schema.tariff_interval import (
    ConsumptionInterval,
    DemandInterval,
    TariffInterval,
)


class GenericTariff(DefinedInterval, Generic[MetricType]):
    """A GenericTariff is a closed datetime interval from [start, end]"""

    children: Optional[tuple[TariffInterval, ...]] = None

    @pa.check_types
    def apply(self, meter_profile: DataFrame[MeterProfileSchema]) -> DataFrame[TariffCostSchema]:
        raise NotImplementedError


class ConsumptionTariff(GenericTariff[Consumption]):
    """A ConsumptionTariff is a closed datetime interval from [start, end]"""

    children: Optional[tuple[ConsumptionInterval, ...]] = None

    @pa.check_types
    def apply(self, meter_profile: DataFrame[MeterProfileSchema]) -> DataFrame[TariffCostSchema]:
        """In the generic case, a ConsumptionTariff is defined over [start, end] and has any
        number of non-overlapping children, which are defined over [start_time, end_time) on
        days_applied and associated with some rate, which itself may contain any number of
        non-overlapping blocks.

        The cost at any datetime in the meter_profile.idx in [start, end] is thus just the rate
        at that datetime (or None).
        """

        # always resample to 1T
        meter_profile = resample(meter_profile)

        if self.children is None or len(self.children) == 0:
            meter_profile[["total_cost", "import_cost", "export_cost", "billed_total_cost"]] = float(0)
            return meter_profile  # type: ignore

        meter_profile[["import_cost", "export_cost"]] = float(0)

        # NOTE there are optimisations we can do here if we know the index and the child intervals are sorted
        # also some low-hanging vectorisations probably
        for ctime in meter_profile.index:
            for intvl in self.children:
                if ctime in intvl:
                    # get block in charge that overlaps [from_quantity, to_quantity)
                    for bl in intvl.charge.blocks:
                        if bl.from_quantity <= meter_profile["cum_profile"].loc[ctime] < bl.to_quantity:
                            nstr = "import" if isinstance(bl, ImportConsumptionBlock) else "export"
                            # apply cost at ctime
                            meter_profile[f"{nstr}_cost"].loc[ctime] = (
                                bl.rate.value * meter_profile["profile"].loc[ctime]  # type: ignore
                            )  # TODO bl can be None?
                            break

        meter_profile["total_cost"] = (meter_profile.import_cost + meter_profile.export_cost).astype(float)
        meter_profile["billed_total_cost"] = float(0)  # TODO NotImplemented

        return meter_profile  # type: ignore  # TODO this warning is inconvenient but correct


class DemandTariff(GenericTariff[Demand]):
    """A ConsumptionTariff is a closed datetime interval from [start, end]"""

    children: Optional[tuple[DemandInterval, ...]] = None

    @pa.check_types
    def apply(self, meter_profile: DataFrame[MeterProfileSchema]) -> DataFrame[TariffCostSchema]:
        raise NotImplementedError
