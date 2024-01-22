from datetime import datetime
from typing import Generic, Optional

import pandera as pa
from pandera.typing import DataFrame
from utal._internal.defined_interval import DefinedInterval
from utal._internal.generic_types import MetricType
from utal._internal.meter_profile import MeterProfileSchema, TariffCostSchema, resample
from utal._internal.tariff_interval import TariffInterval


class GenericTariff(DefinedInterval, Generic[MetricType]):
    """A GenericTariff is a generalised model of an electrical tariff defined as a closed
    timezone-aware datetime interval. It contains child TariffIntervals, which are right-open
    timezone-aware time intervals which are levied on their DaysApplied and associated with a
    single TariffCharge.

    A TariffCharge contains a tuple of TariffBlocks, each of which define the right-open interval
    of some unit over which a given TariffRate is to be applied."""

    children: Optional[tuple[TariffInterval[MetricType], ...]] = None

    @pa.check_types
    def apply(
        self, meter_profile: DataFrame[MeterProfileSchema], billing_start: datetime | None
    ) -> DataFrame[TariffCostSchema]:
        """"""

        # NOTE that in order to apply reset logic, we need to know the start of the first billing period
        # but this should be passed whenever we apply a Profile to the Tariff. If no billing_start is
        # provided, we will infer it from the earliest time in the meter_profile

        # Always resample to 1T. Note that it is only appropriate to use the resampled profile to calculate
        # energy usage over some period, not power, because resampling will average out the peak
        # power statistics. Note also that resampling to 1T will be problematic is the user provides e.g. 1 year of
        # usage = ~526k rows
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
                        # TODO below line is wrong. Only correct when billed once at end of profile.
                        # e.g. what if the blocks reset monthly, but we still levy using usage stats from previous
                        # months? That would be overcharged.
                        if bl.from_quantity <= meter_profile["cum_profile"].loc[ctime] < bl.to_quantity:
                            nstr = "import"  # "import" if isinstance(bl, ImportConsumptionBlock) else "export"  # TODO wrong, direction is now in charge  # noqa
                            # apply cost at ctime
                            meter_profile[f"{nstr}_cost"].loc[ctime] = (
                                bl.rate.value * meter_profile["profile"].loc[ctime]  # type: ignore
                            )  # TODO bl can be None?
                            break

        meter_profile["total_cost"] = (meter_profile.import_cost + meter_profile.export_cost).astype(float)
        meter_profile["billed_total_cost"] = float(0)  # TODO NotImplemented

        return meter_profile  # type: ignore  # TODO this warning is inconvenient but correct
