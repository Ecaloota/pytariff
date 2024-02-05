import pandas as pd
from typing import Iterable, Union
from pandera import dtypes
from pandera.engines import pandas_engine


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
            return all(data_container.map(lambda x: x.tzinfo is not None))
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
                data_container = data_container.map(lambda x: pd.to_datetime(x))

                # we know at least one indice is naive
                if not all(data_container.map(lambda x: x.tzinfo is not None)):
                    return data_container
                data_container = data_container.tz_convert("UTC")
            except Exception:
                pass

        return data_container
