from datetime import date, datetime, timezone
from typing import Generic, Optional
from zoneinfo import ZoneInfo
import pandas as pd

from pydantic import model_validator
from pytariff.core.charge import TariffCharge
from pytariff._internal.defined_interval import DefinedInterval
from pytariff.core.dataframe.profile import MeterProfileHandler
from pytariff.core.typing import MetricType
from pytariff.core.unit import TradeDirection, TariffUnit
from pytariff.core.interval import TariffInterval


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

    @model_validator(mode="after")
    def validate_children_share_charge_resolution(self) -> "GenericTariff":
        if not len(set([x.charge.resolution for x in self.children])) == 1:
            raise ValueError
        return self

    def apply_to(
        self,
        profile_handler: MeterProfileHandler,
        profile_unit: TariffUnit,
    ) -> pd.DataFrame:
        """"""

        def _block_map_name(charge: TariffCharge) -> str:

            direction = "_null_direction" if not charge.unit.direction else charge.unit.direction.value.lower()
            prefix = f"_{direction}_profile_usage"
            suffix = f"_{charge.method.value.lower()}"
            return prefix + suffix

        def _cost_import_value(
            idx: datetime, charge: TariffCharge, applied_map: pd.DataFrame, charge_profile: pd.DataFrame
        ) -> float:
            """Given the index of the cost_df, map that index to the block rate value"""
            # If the block.rate is a TariffRate, idx is unused, else it defines the
            # value of the block rate at time idx for a MarketRate
            # NOTE the cost at time idx is the value of the relevant profile column
            # at idx * block.rate.get_value(idx)

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

        child_resolution = [x.charge.resolution for x in self.children][0]
        resampled_meter = profile_handler._pytariff_resample(profile_handler.profile, child_resolution)
        tariff_start = self.start  # needed to calculate reset_period start

        for child in self.children:
            if child.charge.unit.metric != profile_unit.metric:
                # TODO return zeroed charge_profile -- no charge can be levied on different metrics
                pass

            # resample the meter profile given charge information
            charge_profile = profile_handler._pytariff_resample(
                profile_handler.profile, child_resolution, window=child.charge.window
            )

            # calculate the cumulative profile including reset_period tracking given charge information
            # also split the profile into _import and _export quantities so we can determine cost sign for given charge
            charge_profile = profile_handler._pytariff_transform(charge_profile, tariff_start, child.charge)

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

            if len(charge_profile.index) != len(resampled_meter.index):
                raise ValueError("Tariff misalignment")

            resampled_meter[f"cost_import_{child.uuid}"] = charge_profile.filter(like="cost_import").sum(axis=1)
            resampled_meter[f"cost_export_{child.uuid}"] = charge_profile.filter(like="cost_export").sum(axis=1)

        resampled_meter["import_cost"] = resampled_meter.filter(like="cost_import").sum(axis=1)
        resampled_meter["export_cost"] = resampled_meter.filter(like="cost_export").sum(axis=1)
        resampled_meter["total_cost"] = resampled_meter["import_cost"] + resampled_meter["export_cost"]

        return resampled_meter
