from zoneinfo import ZoneInfo

import pandas as pd
import pytest
from pandera.errors import SchemaError

from utal.schema.meter_profile import MeterProfileSchema


@pytest.mark.parametrize(
    "data, raises",
    [
        (
            pd.DataFrame(
                index=[pd.Timestamp(2023, 1, 1, tzinfo=ZoneInfo("Australia/Brisbane"), unit="ns")],
                data={"profile": 1.0},
            ),
            False,
        ),
        (
            pd.DataFrame(
                index=[pd.Timestamp(2023, 1, 1, tzinfo=ZoneInfo("UTC"), unit="us")],
                data={"profile": 1.0},
            ),
            False,
        ),
        (
            pd.DataFrame(
                index=[pd.Timestamp(2023, 1, 1, tzinfo=ZoneInfo("UTC"))],
                data={"profile": 1.0},
            ),
            False,
        ),
        (  # index is not tz-aware
            pd.DataFrame(
                index=[pd.Timestamp(2023, 1, 1)],
                data={"profile": 1.0},
            ),
            True,
        ),
        (  # profile value is an int, not a float
            pd.DataFrame(
                index=[pd.Timestamp(2023, 1, 1)],
                data={"profile": 1},
            ),
            True,
        ),
        (  # index is pd.to_datetime() coercible and tz-aware (and therefore valid)
            pd.DataFrame(
                index=["2023-01-01T00:00:00+00:00"],
                data={"profile": 1.0},
            ),
            False,
        ),
        (  # index is pd.to_datetime() coercible but not tz-aware (and therefore invalid)
            pd.DataFrame(
                index=["2023-01-01T00:00:00"],
                data={"profile": 1.0},
            ),
            True,
        ),
        (  # different valid tzs are invalid, and Timestamp is naive, so this fails
            pd.DataFrame(
                index=["2023-01-01T00:00:00", pd.Timestamp(2023, 1, 1, 1)],
                data={"profile": [1.0, 1.0]},
            ),
            True,
        ),
        (  # different valid tzs are invalid
            pd.DataFrame(
                index=["2023-01-01T00:00:00+00:00", pd.Timestamp(2023, 1, 1, 1, tzinfo=ZoneInfo("UTC"))],
                data={"profile": [1.0, 1.0]},
            ),
            False,
        ),
    ],
)
def test_pandera_meter_profile_type(data, raises: bool):
    """"""

    if raises:
        with pytest.raises(SchemaError):
            MeterProfileSchema.validate(data)
    else:
        MeterProfileSchema.validate(data)
