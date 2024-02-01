from datetime import datetime

import pandas as pd
import pandera as pa
from pandera.typing import Index

from utal.core.charge import TariffCharge
from utal.core.dataframe.extra import AwareDateTime
from utal.core.unit import UsageChargeMethod


class MeterProfileSchema(pa.DataFrameModel):
    idx: Index[AwareDateTime] = pa.Field(coerce=True)
    profile: float


class MeterProfileHandler:
    def __init__(self, profile: pd.DataFrame) -> None:
        self.profile = profile

    # TODO write a decorator which validates types leaving the function?
    def _utal_resample(
        self,
        charge_resolution: str,
        min_resolution: str = "1min",
        window: str | None = None,
    ) -> pd.DataFrame:
        """
        Resample the provided DataFrame, first by sampling at min_resolution and interpolating
        the result, then sampling at the provided charge.resolution.
        """

        if len(self.profile.index) < 2:
            raise ValueError

        window = min_resolution if not window else window
        min_resolution_df = self.profile.resample(min_resolution).interpolate(method="linear")
        resampled = min_resolution_df.rolling(window).mean().resample(charge_resolution).mean()

        try:
            MeterProfileSchema(resampled)
        except Exception:
            raise

        return resampled

    def _utal_calculate_reset_periods(self, charge: TariffCharge, ref_time: datetime) -> pd.DataFrame:
        """"""
        # profile_copy = self.profile.copy()

        if charge.reset_data:
            # NOTE Would occur if user provided metering data that began earlier than tariff definition. In this case,
            # we simply set the reference time to be the earliest time in the index, assuming the index is ordered.
            if self.profile.index[0] < ref_time:
                ref_time = self.profile.index[0]

            self.profile["reset_periods"] = self.profile.index.to_series().apply(
                charge.reset_data.period.count_occurences, reference=ref_time
            )
        else:
            self.profile["reset_periods"] = 1

        try:
            MeterProfileSchema(self.profile)
        except Exception:
            raise

        return self.profile

    def _utal_transform(self, tariff_start: datetime, charge: TariffCharge) -> pd.DataFrame:
        """Calculate properties of the provided dataframe that are useful for tariff application.
        Specifically, divide the profile into _import and _export quantities, and calculate cumulative
        profiles for each, such that it is possible to determine costings for the given charge.

        By convention, the quantity imported or exported is defined to be positive in the _import_profile and
        _export_profile columns, respectively.
        """

        # profile_copy = self.profile.copy()

        self.profile["_import_profile_usage"] = self.profile["profile"].apply(
            lambda x: charge.unit.convention._import_sign() * x if charge.unit.convention._is_import(x) else 0
        )
        self.profile["_export_profile_usage"] = self.profile["profile"].apply(
            lambda x: charge.unit.convention._export_sign() * x if charge.unit.convention._is_export(x) else 0
        )

        self.profile = self._utal_calculate_reset_periods(charge, tariff_start)

        # NOTE should be vectorised one day
        for profile_direction in ["_import_profile_usage", "_export_profile_usage"]:
            for method in [
                UsageChargeMethod.mean,
                UsageChargeMethod.cumsum,
                UsageChargeMethod.max,
                UsageChargeMethod.identity,
            ]:
                req_transform = method.value if method.value != "identity" else lambda x: x
                self.profile[f"{profile_direction}_{method.value}"] = self.profile.groupby(
                    self.profile["reset_periods"]
                ).transform(req_transform)[profile_direction]

        try:
            MeterProfileSchema(self.profile)
        except Exception:
            raise

        return self.profile
