from datetime import date, datetime, timezone
from typing import Generic, Optional
from zoneinfo import ZoneInfo
import pandas as pd

import pandera as pa
from pandera.typing import DataFrame
from utal._internal.defined_interval import DefinedInterval
from utal._internal.generic_types import MetricType, SignConvention
from utal._internal.meter_profile import MeterProfileSchema, TariffCostSchema, meter_statistics, resample
from utal._internal.tariff_interval import TariffInterval
from utal._internal.unit import TariffUnit


class GenericTariff(DefinedInterval, Generic[MetricType]):
    """A GenericTariff is a generalised model of an electrical tariff defined as a closed
    timezone-aware datetime interval. It contains child TariffIntervals, which are right-open
    timezone-aware time intervals which are levied on their DaysApplied and associated with a
    single TariffCharge.

    A TariffCharge contains a tuple of TariffBlocks, each of which define the right-open interval
    of some unit over which a given TariffRate is to be applied."""

    children: tuple[TariffInterval[MetricType], ...]

    def __contains__(self, other: datetime | date, tzinfo: Optional[timezone | ZoneInfo] = None) -> bool:
        is_defined_contained = super(GenericTariff, self).__contains__(other, tzinfo)
        is_child_contained = any(child.__contains__(other) for child in self.children)
        return is_defined_contained and is_child_contained

    @pa.check_types
    def apply(
        self, meter_profile: DataFrame[MeterProfileSchema], billing_start: datetime | None, profile_unit: TariffUnit
    ) -> DataFrame[TariffCostSchema]:
        """"""

        # NOTE that in order to apply reset logic, we need to know the start of the first billing period
        # but this should be passed whenever we apply a Profile to the Tariff. If no billing_start is
        # provided, we will infer it from the earliest time in the meter_profile

        # Always resample to 1T. Note that it is only appropriate to use the resampled profile to calculate
        # energy usage over some period, not power, because resampling will average out the peak
        # power statistics. Note also that resampling to 1T will be problematic is the user provides e.g. 1 year of
        # usage = ~526k rows

        # NOTE in order to resample, we need to know the resampling method
        # and we need to know the desired resolution. Iff the resampling method is rolling_mean,
        # we need to know the rolling window size. But these all depend on the charge being considered
        # so we need to resample potentially once for each unique set of these parameters?

        for child in self.children:
            if child.charge.unit.metric != profile_unit.metric:
                # TODO return zeroed charge_profile -- no charge can be levied on different metrics
                pass

            # TODO verify sign parity here, this is just a filler
            # sign_parity = 1 if profile_unit.convention == SignConvention.Passive else -1

            # resample the meter profile given charge information
            charge_profile = resample(meter_profile, child.charge)

            # calculate the cumulative profile including reset_period tracking given charge information
            # also split the profile into _import and _export quantities so we can determine cost sign for given charge
            charge_profile = transform(charge_profile, child.charge, billing_start, profile_unit)

            # calculate stats for original meter profile given charge resolution. keep this information so we know
            # how to apply demand charges, for example
            charge_statistics = meter_statistics(meter_profile, child.charge)

            # The charge map denotes whether the charge profile indices are contained within the meter profile given
            charge_map = charge_profile.index.map(self.__contains__)
            # NOTE the charge used to generate the charge_map has an uuid associated with it

            for block in child.charge.blocks:
                block_map = charge_profile.cum_profile.map(block.__contains__)
                # NOTE the block used to generate the block_map has an uuid associated with it

                # Where both charge_map and block map are True, cost at index is block rate
                # TODO work out the correct types here
                charge_profile.loc[charge_map & block_map, "foo"] = block.rate.value  # type: ignore

                # We can identify this map identifier by the combination of the:
                # charge uuid + block uuid = 64 chars
                # which pseudo-uniquely (~1/(billion**2)) identifies the combination used to assign the rate
                print("foo")

            # TODO find a way to vectorise the value mapping onto a dataframe...
            # each time in the charge_profile index maps to exactly one rate in the current charge
            # which is either zero or the charge value, if active
            # A charge against some quantity Q is applied at some given time T iff:
            # 1. T is in the parent DefinedInterval [start, end] -- NOTE we have the __contains__ for this already
            # 2. T in in the self AppliedInterval [start_time, end_time) & days_applied -- NOTE we have __contains__ for this
            # 3. Q is in the units of child.charge.unit - NOTE easy enough
            # 4. The cumulative sum of Q from the last reset_period start to T is in
            # [from_quantity, to_quantity) of one of the child.charge.blocks -- should be okay

            # If these are all True, the charge levied at time T on quantity Q is the TariffRate
            # associated with the active block
            # NOTE check the sign alignment against the charge SignConvention and the profile SignConvention

        # meter_profile[["import_cost", "export_cost"]] = float(0)
        # meter_profile["total_cost"] = (meter_profile.import_cost + meter_profile.export_cost).astype(float)
        # meter_profile["billed_total_cost"] = float(0)  # TODO NotImplemented

        return meter_profile  # type: ignore  # TODO this warning is inconvenient but correct
