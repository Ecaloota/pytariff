from datetime import datetime
from typing import Hashable, Iterable, Literal, Union

import numpy as np
import pandas as pd
import pandera as pa
from pandera import dtypes
from pandera.engines import pandas_engine
from pandera.typing import Index, DataFrame

from utal._internal.charge import TariffCharge
from utal._internal.generic_types import SignConvention
from utal._internal.unit import TariffUnit


@pandas_engine.Engine.register_dtype()
@dtypes.immutable
class AwareDateTime(pandas_engine.DateTime):
    """
    As of writing, 15 Nov '23, Pandera doesn't support the notion of 'any tz-aware datetime',
    and requires a specific timezone to be declared at schema definition.

    In our case, we do not care if the user provides any particular timezone, or combination of
    timezones, as long as each entry has an associated timezone.

    An alternative approach could involve allowing even naive datetimes and assuming the data is
    in UTC, but this seems better.
    """

    def check(
        self, pandera_dtype: dtypes.DataType, data_container: pd.Series | pd.DataFrame | None = None
    ) -> Union[bool, Iterable[bool]]:
        """"""

        if data_container is None:
            return False

        try:
            # assert each k in the index is aware;
            # accepts col with dytpe 'object' and mixed format timezones
            return all(data_container.map(lambda x: x.tzinfo is not None))  # type: ignore
        except Exception:
            pass

        return False

    def coerce(self, data_container: pd.Series | pd.DataFrame) -> pd.Series | pd.DataFrame:
        """Coerce a pandas.Series to timezone aware datetimes in UTC iff the column is datetime64
        or derived type or otherwise if the column is to_datetime coercible; will only convert
        tz-aware datetimes to their UTC equivalent -- any naive times are left,
        which will cause the self.check method to fail validation"""

        # if index is known datetime64-derived dtype, we only need to check for awareness
        # and convert to UTC iff aware
        if pd.api.types.is_datetime64_any_dtype(data_container):
            try:
                data_container = data_container.tz_convert("UTC")
            except TypeError:
                pass

        else:
            try:
                # map is required, as call on Series is future deprecated
                data_container = data_container.map(lambda x: pd.to_datetime(x))  # type: ignore

                # we know at least one indice is naive
                if not all(data_container.map(lambda x: x.tzinfo is not None)):
                    return data_container
                data_container = data_container.tz_convert("UTC")
            except Exception:
                pass

        return data_container


class MeterProfileSchema(pa.DataFrameModel):
    idx: Index[AwareDateTime] = pa.Field(coerce=True)
    profile: float


class TariffCostSchema(MeterProfileSchema):
    total_cost: float  # the sum of import cost + export cost
    import_cost: float  # the amount paid due to import
    export_cost: float  # the amount paid due to export (negative value is revenue generated)
    billed_total_cost: float  # the cumulative billed amount, levied at each billing interval


@pa.check_types
def resample(
    df: DataFrame[MeterProfileSchema], charge: TariffCharge, min_resolution: str = "1min"
) -> MeterProfileSchema:
    """
    Resample the provided DataFrame, first by sampling at min_resolution and interpolating
    the result, then sampling at the provided charge.resolution.

    NOTE This approach is undesirable when the minimum resolution (default = '1min') is less than the implied resolution
    of the provided DataFrame.
    """

    if len(df.index) < 2:
        raise ValueError

    min_resolution_df = df.resample(min_resolution).interpolate(method="linear")
    resampled = min_resolution_df.resample(charge.resolution).mean()
    new_df = MeterProfileSchema(resampled)

    return new_df


# TODO prescribe the returned dict more strictly: it should have specific keys
@pa.check_types
def meter_statistics(df: DataFrame[MeterProfileSchema], charge: TariffCharge) -> dict:
    return {}


@pa.check_types
def transform(
    df: DataFrame[MeterProfileSchema], charge: TariffCharge, billing_start: datetime, meter_unit: TariffUnit
) -> DataFrame[MeterProfileSchema]:
    """Calculate properties of the provided dataframe that are useful for tariff application.
    Specifically, divide the profile into _import and _export quantities, and calculate cumulative
    profiles for each, such that it is possible to determine costings for the given charge."""

    def is_export(value: float) -> bool:
        is_passive_export = meter_unit.convention == SignConvention.Passive and value > 0
        is_active_export = meter_unit.convention == SignConvention.Active and value < 0
        return is_passive_export or is_active_export

    def is_import(value: float) -> bool:
        is_passive_import = meter_unit.convention == SignConvention.Passive and value < 0
        is_active_import = meter_unit.convention == SignConvention.Active and value > 0
        return is_passive_import or is_active_import

    def calculate_reset_periods(start_datetime: datetime) -> DataFrame:
        if charge.reset_period:
            df["reset_periods"] = ((df.index - start_datetime) / pd.to_timedelta(charge.reset_period.value)).astype(int)
        return df

    def calculate_reset_cumsum(col_name: str) -> DataFrame:
        df[f"{col_name}_cumsum"] = df.groupby((df["reset_periods"] != df["reset_periods"].shift()).cumsum())[
            col_name
        ].cumsum()
        return df

    def _import_sign() -> Literal[-1, 1]:
        return -1 if meter_unit.convention == SignConvention.Passive else 1

    def _export_sign() -> Literal[-1, 1]:
        return -1 if meter_unit.convention == SignConvention.Active else 1

    # TODO this whole func needs work -- not robust

    df["_import_profile"] = df["profile"].apply(lambda x: _import_sign() * x if is_import(x) else 0)
    df["_export_profile"] = df["profile"].apply(lambda x: _export_sign() * x if is_export(x) else 0)

    df = calculate_reset_periods(billing_start)
    df = calculate_reset_cumsum("_import_profile")
    df = calculate_reset_cumsum("_export_profile")

    return df

    # resampled["cum_profile"] = resampled.profile.cumsum()
