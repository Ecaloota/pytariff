from datetime import datetime
from typing import Iterable, Literal, Union

import pandas as pd
import pandera as pa
from pandera import dtypes
from pandera.engines import pandas_engine
from pandera.typing import Index, DataFrame

from utal._internal.charge import TariffCharge
from utal._internal.generic_types import SignConvention
from utal._internal.unit import TariffUnit, UsageChargeMethod

import plotly.express as px  # type: ignore


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
    # billed_total_cost: float  # the cumulative billed amount, levied at each billing interval
    # TODO billing is complex. leave it for later


@pa.check_types
def resample(
    df: DataFrame[MeterProfileSchema], charge_resolution: str, min_resolution: str = "1min", window: str | None = None
) -> DataFrame[MeterProfileSchema]:
    """
    Resample the provided DataFrame, first by sampling at min_resolution and interpolating
    the result, then sampling at the provided charge.resolution.

    NOTE This approach is undesirable when the minimum resolution (default = '1min') is less than the implied resolution
    of the provided DataFrame.
    """

    if len(df.index) < 2:
        raise ValueError

    window = min_resolution if not window else window

    min_resolution_df = df.resample(min_resolution).interpolate(method="linear")
    resampled = min_resolution_df.rolling(window).mean().resample(charge_resolution).mean()
    new_df = MeterProfileSchema(resampled)

    return new_df  # type: ignore


@pa.check_types
def transform(  # noqa
    tariff_start: datetime, df: DataFrame[MeterProfileSchema], charge: TariffCharge, meter_unit: TariffUnit
) -> MeterProfileSchema:
    """Calculate properties of the provided dataframe that are useful for tariff application.
    Specifically, divide the profile into _import and _export quantities, and calculate cumulative
    profiles for each, such that it is possible to determine costings for the given charge.

    By convention, the quantity imported or exported is defined to be positive in the _import_profile and
    _export_profile columns, respectively.
    """

    def is_export(value: float) -> bool:
        is_passive_export = meter_unit.convention == SignConvention.Passive and value > 0
        is_active_export = meter_unit.convention == SignConvention.Active and value < 0
        return is_passive_export or is_active_export

    def is_import(value: float) -> bool:
        is_passive_import = meter_unit.convention == SignConvention.Passive and value < 0
        is_active_import = meter_unit.convention == SignConvention.Active and value > 0
        return is_passive_import or is_active_import

    def calculate_reset_periods(ref_time: datetime) -> DataFrame:
        if charge.reset_data:
            # NOTE Would occur if user provided metering data that began earlier than tariff definition. In this case,
            # we simply set the reference time to be the earliest time in the index, assuming the index is ordered.
            if df.index[0] < ref_time:
                ref_time = df.index[0]

            df["reset_periods"] = df.index.to_series().apply(
                charge.reset_data.period.count_occurences, reference=ref_time
            )
        else:
            df["reset_periods"] = 1

        return df

    def calculate_profile_transformation(col_name: str, transform: UsageChargeMethod) -> DataFrame:
        """Calculate the mean/max/cumsum of col_name in given DataFrame and broadcast the value
        to the DataFrame grouped by reset_periods.

        NOTE for example, given transform_name == UsageChargeMethod.mean with two unique reset_period
        indices in the given DataFrame will return a new column on that DataFrame with the mean
        usage of that unit (in a given direction) _for each reset_period_.
        """

        req_transform = transform.value if transform.value != "identity" else lambda x: x
        df[f"{col_name}_{transform.value}"] = df.groupby(df["reset_periods"]).transform(req_transform)[col_name]
        return df

    def _import_sign() -> Literal[-1, 1]:
        return -1 if meter_unit.convention == SignConvention.Passive else 1

    def _export_sign() -> Literal[-1, 1]:
        return -1 if meter_unit.convention == SignConvention.Active else 1

    # TODO this whole func needs work

    df["_import_profile_usage"] = df["profile"].apply(lambda x: _import_sign() * x if is_import(x) else 0)
    df["_export_profile_usage"] = df["profile"].apply(lambda x: _export_sign() * x if is_export(x) else 0)

    df = calculate_reset_periods(ref_time=tariff_start)

    # NOTE should be vectorised one day
    for profile_direction in ["_import_profile_usage", "_export_profile_usage"]:
        for method in [
            UsageChargeMethod.mean,
            UsageChargeMethod.cumsum,
            UsageChargeMethod.max,
            UsageChargeMethod.identity,
        ]:
            df = calculate_profile_transformation(profile_direction, method)

    return MeterProfileSchema(df)


@pa.check_types
def plot(df: DataFrame[TariffCostSchema], include_additional_cost_components: bool = False) -> None:
    """"""

    if not include_additional_cost_components:
        df = df[["import_cost", "export_cost", "total_cost"]]  # type: ignore

    fig = px.line(df)
    fig.show()


# def num_billing_events(billing_data: BillingData, meter_end: datetime) -> int:
#     """"""

#     current_dt = billing_data.start
#     billing_events = 0

#     while current_dt <= meter_end:
#         billing_events += 1
#         delta_time: str = billing_data.frequency._to_days(current_dt)

#         if billing_data.frequency._is_day_suffix():
#             as_int = int(delta_time.replace("D", ""))
#             current_dt += timedelta(days=as_int)

#         else:
#             raise NotImplementedError

#     return billing_events
