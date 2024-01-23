from typing import Hashable, Iterable, Union

import numpy as np
import pandas as pd
import pandera as pa
from pandera import dtypes
from pandera.engines import pandas_engine
from pandera.typing import Index, DataFrame


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
def resample(df: DataFrame[MeterProfileSchema]) -> DataFrame[MeterProfileSchema]:
    """"""

    if len(df.index) < 2:
        raise ValueError

    # get the index keys for each unique value in the resample.groups dict
    # these will tell us which keys were anchored against in the resample
    inverted: dict[list[Hashable], list[Hashable]] = {}
    for k, v in df.resample("1min").groups.items():  # TODO wrong, we want to resample out beyond last anchor too
        if v in inverted:
            inverted[v].append(k)
        else:
            inverted[v] = [k]

    # replace nan with zero in resampled object
    resampled = df.resample("1min").asfreq().fillna(0)

    # take mean of df slice for each slice in the index keys found before
    for k, v in inverted.items():  # type: ignore
        resampled.loc[inverted[k]] = np.sum(resampled.profile.loc[inverted[k]]) / len(v)  # type: ignore

    # keep the cumulative profile, we will need it
    resampled["cum_profile"] = resampled.profile.cumsum()

    return resampled  # type: ignore
