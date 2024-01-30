from datetime import date, datetime, timezone
from typing import Generic, Optional
from zoneinfo import ZoneInfo
import pandas as pd

import pandera as pa
from pandera.typing import DataFrame
from utal._internal.charge import TariffCharge
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
        self,
        meter_profile: DataFrame[MeterProfileSchema],
        profile_unit: TariffUnit,
    ) -> DataFrame[TariffCostSchema]:
        """"""

        def _block_map_name(charge: TariffCharge) -> str:
            prefix = f"_{charge.unit.direction.value.lower()}_profile"
            suffix = f"_{charge.method.value.lower()}"
            return prefix + suffix

        def _cost_import_value(
            idx: datetime, charge: TariffCharge, applied_map: pd.DataFrame, charge_profile: pd.DataFrame
        ) -> float:
            """Given the index of the cost_df, map that index to the block rate value"""
            # If the block.rate is a TariffRate, idx is unused, else it defines the
            # value of the block rate at time idx for a MarketRate
            if charge.unit.direction == TradeDirection.Import and block.rate and applied_map[idx]:
                return block.rate.get_value(idx) * getattr(charge_profile, _block_map_name(charge)).loc[idx]
            return 0.0

        def _cost_export_value(
            idx: datetime, charge: TariffCharge, applied_map: pd.DataFrame, charge_profile: pd.DataFrame
        ) -> float:
            """Given the index of the cost_df, map that index to the block rate value"""
            # if the block.rate is a TariffRate, idx is unused, else it defines the
            # value of the block rate at time idx for a MarketRate
            if charge.unit.direction == TradeDirection.Export and block.rate and applied_map[idx]:
                return block.rate.get_value(idx) * getattr(charge_profile, _block_map_name(charge)).loc[idx]
            return 0.0

        min_resolution = "1min"
        resampled_meter = resample(meter_profile, min_resolution, window=None)
        tariff_start = self.start  # needed to calculate reset_period start

        for child in self.children:
            if child.charge.unit.metric != profile_unit.metric:
                # TODO return zeroed charge_profile -- no charge can be levied on different metrics
                pass

            # resample the meter profile given charge information
            charge_profile = resample(meter_profile, child.charge.resolution, window=child.charge.window)

            # calculate the cumulative profile including reset_period tracking given charge information
            # also split the profile into _import and _export quantities so we can determine cost sign for given charge
            charge_profile = transform(tariff_start, charge_profile, child.charge, profile_unit)  # type: ignore

            # The charge map denotes whether the charge profile indices are contained within the meter profile given
            charge_map = charge_profile.index.map(self.__contains__)

            for block in child.charge.blocks:
                cost_df = pd.DataFrame(index=charge_profile.index, data={"cost": 0})
                uuid_identifier = str(child.charge.uuid) + str(block.uuid)

                block_map = getattr(charge_profile, _block_map_name(child.charge)).map(block.__contains__)
                applied_map = charge_map & block_map
                cost_df["cost_import"] = cost_df.index.map(
                    lambda x: _cost_import_value(
                        x, charge=child.charge, applied_map=applied_map, charge_profile=charge_profile
                    )
                )
                cost_df["cost_export"] = cost_df.index.map(
                    lambda x: _cost_export_value(
                        x, charge=child.charge, applied_map=applied_map, charge_profile=charge_profile
                    )
                )

                charge_profile[f"cost_import_{uuid_identifier}"] = cost_df["cost_import"]
                charge_profile[f"cost_export_{uuid_identifier}"] = cost_df["cost_export"]

            # match indices on resampled charge_profile onto resampled_meter
            resamp_charge_profile = resample(charge_profile, min_resolution, window=None)  # TODO this causes issues
            resampled_meter[f"cost_import_{child.uuid}"] = resamp_charge_profile.filter(like="cost_import").sum(axis=1)
            resampled_meter[f"cost_export_{child.uuid}"] = resamp_charge_profile.filter(like="cost_export").sum(axis=1)

        # NOTE this is not the cumsum of the cost till index idx, but the sum of import/export cost at index idx
        resampled_meter["import_cost"] = resampled_meter.filter(like="cost_import").sum(axis=1)
        resampled_meter["export_cost"] = resampled_meter.filter(like="cost_export").sum(axis=1)
        resampled_meter["total_cost"] = resampled_meter["import_cost"] + resampled_meter["export_cost"]

        # billed total_cost is the total_cost taken stepwise from billing_data.start
        # and stepped with billing_data.frequency

        # given the frequency, the start, and the final index of the sorted resampled_meter
        # we know how many we need to bill the resampled_meter. NOTE previous sentence doesnt account for partial
        # billing periods. See: test_num_billing_events

        # resampled_meter["billed_total_cost"] = 0.0  # TODO this is complex. resolve later

        return resampled_meter  # type: ignore
