from datetime import date, datetime, timezone
from typing import Generic, Optional
from zoneinfo import ZoneInfo
import pandas as pd

import pandera as pa
from pandera.typing import DataFrame
from utal._internal.defined_interval import DefinedInterval
from utal._internal.generic_types import MetricType, TradeDirection
from utal._internal.meter_profile import MeterProfileSchema, TariffCostSchema, resample, transform
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

        # TODO We are going to need to address these type ignores...

        # NOTE in order to resample, we need to know the resampling method
        # and we need to know the desired resolution. Iff the resampling method is rolling_mean,
        # we need to know the rolling window size. But these all depend on the charge being considered
        # so we need to resample potentially once for each unique set of these parameters?
        min_resolution = "1min"
        resampled_meter = resample(meter_profile, min_resolution)

        for child in self.children:
            if child.charge.unit.metric != profile_unit.metric:
                # TODO return zeroed charge_profile -- no charge can be levied on different metrics
                pass

            # resample the meter profile given charge information
            charge_profile = resample(meter_profile, child.charge.resolution)

            # calculate the cumulative profile including reset_period tracking given charge information
            # also split the profile into _import and _export quantities so we can determine cost sign for given charge
            charge_profile = transform(charge_profile, child.charge, billing_start, profile_unit)  # type: ignore # TODO

            # The charge map denotes whether the charge profile indices are contained within the meter profile given
            charge_map = charge_profile.index.map(self.__contains__)  # type: ignore

            for block in child.charge.blocks:
                cost_df = pd.DataFrame(index=charge_profile.index, data={"cost": 0})  # type: ignore
                uuid_identifier = str(child.charge.uuid) + str(block.uuid)

                # TODO this is only true if being charged on cumulative amount, not so if being charged on max of
                # quantity within reset_period or mean, for example. Need a method which enumerates the possibilities
                # cleanly to select the correct charge_profile column
                if child.charge.unit.direction == TradeDirection.Import:
                    block_map = charge_profile._import_profile_cumsum.map(block.__contains__)  # type: ignore
                    cost_df.loc[charge_map & block_map, "cost_import"] = block.rate.get_value()  # type: ignore
                    cost_df.loc[charge_map & block_map, "cost_export"] = 0  # type: ignore

                elif child.charge.unit.direction == TradeDirection.Export:
                    block_map = charge_profile._export_profile_cumsum.map(block.__contains__)  # type: ignore
                    cost_df.loc[charge_map & block_map, "cost_import"] = 0  # type: ignore
                    cost_df.loc[charge_map & block_map, "cost_export"] = block.rate.get_value()  # type: ignore

                charge_profile[f"cost_import_{uuid_identifier}"] = cost_df["cost_import"]  # type: ignore
                charge_profile[f"cost_export_{uuid_identifier}"] = cost_df["cost_export"]  # type: ignore

            # match indices on resampled charge_profile onto resampled_meter
            resamp_charge_profile = resample(charge_profile, min_resolution)  # type: ignore
            resampled_meter[f"cost_import_{child.uuid}"] = resamp_charge_profile.filter(like="cost_import").sum(axis=1)  # type: ignore  # noqa
            resampled_meter[f"cost_export_{child.uuid}"] = resamp_charge_profile.filter(like="cost_export").sum(axis=1)  # type: ignore  # noqa

        resampled_meter["import_cost"] = resampled_meter.filter(like="cost_import").sum(axis=1)  # type: ignore
        resampled_meter["export_cost"] = resampled_meter.filter(like="cost_export").sum(axis=1)  # type: ignore
        resampled_meter["total_cost"] = resampled_meter["import_cost"] + resampled_meter["export_cost"]  # type: ignore

        return resampled_meter  # type: ignore  # TODO this warning is inconvenient but correct
