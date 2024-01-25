from datetime import datetime
from zoneinfo import ZoneInfo

from unittest import mock
import numpy as np

import pandas as pd
import pytest
from pandera.errors import SchemaError
from utal._internal.charge import TariffCharge
from utal._internal.generic_types import SignConvention

from utal._internal.meter_profile import MeterProfileSchema, resample, transform
from utal._internal.period import ConsumptionResetPeriod
from utal._internal.unit import TariffUnit


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
        (  # profile cannot contain nan
            pd.DataFrame(
                index=[pd.Timestamp(2023, 1, 1, tzinfo=ZoneInfo("Australia/Brisbane"), unit="ns")],
                data={"profile": np.nan},
            ),
            True,
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


@pytest.mark.parametrize(
    "data, charge, expected_resampled_list, raises",
    [
        (
            pd.DataFrame(
                index=[
                    pd.Timestamp(year=2023, month=1, day=1, hour=0, minute=0, tzinfo=ZoneInfo("UTC"), unit="ns"),
                    pd.Timestamp(year=2023, month=1, day=1, hour=0, minute=1, tzinfo=ZoneInfo("UTC"), unit="ns"),
                ],
                data={"profile": [0.0, 1.0]},
            ),
            mock.Mock(spec=TariffCharge, resolution="5min"),
            [0.5],
            False,
        ),
        (
            pd.DataFrame(
                index=[
                    pd.Timestamp(year=2023, month=1, day=1, hour=0, minute=0, tzinfo=ZoneInfo("UTC"), unit="ns"),
                    pd.Timestamp(year=2023, month=1, day=1, hour=0, minute=5, tzinfo=ZoneInfo("UTC"), unit="ns"),
                ],
                data={"profile": [0.0, 2.0]},
            ),
            mock.Mock(spec=TariffCharge, resolution="5min"),
            [0.8, 2.0],
            False,
        ),
        (
            pd.DataFrame(
                index=[
                    pd.Timestamp(year=2023, month=1, day=1, hour=0, minute=0, tzinfo=ZoneInfo("UTC"), unit="ns"),
                    pd.Timestamp(year=2023, month=1, day=1, hour=0, minute=2, tzinfo=ZoneInfo("UTC"), unit="ns"),
                    pd.Timestamp(year=2023, month=1, day=1, hour=0, minute=4, tzinfo=ZoneInfo("UTC"), unit="ns"),
                ],
                data={"profile": [0.0, 2.0, 0.0]},
            ),
            mock.Mock(spec=TariffCharge, resolution="1min"),
            [0.0, 1.0, 2.0, 1.0, 0.0],
            False,
        ),
        (
            pd.DataFrame(
                index=[
                    pd.Timestamp(year=2023, month=1, day=1, hour=0, minute=0, tzinfo=ZoneInfo("UTC"), unit="ns"),
                    pd.Timestamp(year=2023, month=1, day=1, hour=0, minute=2, tzinfo=ZoneInfo("UTC"), unit="ns"),
                    pd.Timestamp(year=2023, month=1, day=1, hour=0, minute=4, tzinfo=ZoneInfo("UTC"), unit="ns"),
                ],
                data={"profile": [0.0, 2.0, 0.0]},
            ),
            mock.Mock(spec=TariffCharge, resolution="5min"),
            [0.8],
            False,
        ),
        (
            pd.DataFrame(
                index=[
                    pd.Timestamp(year=2023, month=1, day=1, hour=0, minute=0, tzinfo=ZoneInfo("UTC"), unit="ns"),
                    pd.Timestamp(year=2023, month=1, day=1, hour=0, minute=5, tzinfo=ZoneInfo("UTC"), unit="ns"),
                    pd.Timestamp(year=2023, month=1, day=1, hour=0, minute=10, tzinfo=ZoneInfo("UTC"), unit="ns"),
                ],
                data={"profile": [0.0, 10.0, -10.0]},
            ),
            mock.Mock(spec=TariffCharge, resolution="5min"),
            [4.0, 2.0, -10.0],
            False,
        ),
    ],
)
def test_meter_profile_schema_resample_method(
    data: pd.DataFrame, charge: TariffCharge, expected_resampled_list: list[float], raises: bool
) -> None:
    """TODO"""

    resampled = resample(data, charge)
    assert list(resampled.profile) == expected_resampled_list


@pytest.mark.parametrize(
    "data, charge, billing_start, meter_unit, exp_import_profile, exp_export_profile, exp_cumsum_import, exp_cumsum_export",
    [
        (
            pd.DataFrame(
                index=[
                    pd.Timestamp(year=2023, month=1, day=1, hour=0, minute=0, tzinfo=ZoneInfo("UTC"), unit="ns"),
                    pd.Timestamp(year=2023, month=1, day=1, hour=0, minute=1, tzinfo=ZoneInfo("UTC"), unit="ns"),
                    pd.Timestamp(year=2023, month=1, day=1, hour=0, minute=2, tzinfo=ZoneInfo("UTC"), unit="ns"),
                    pd.Timestamp(year=2023, month=1, day=1, hour=0, minute=3, tzinfo=ZoneInfo("UTC"), unit="ns"),
                    pd.Timestamp(year=2023, month=1, day=1, hour=0, minute=4, tzinfo=ZoneInfo("UTC"), unit="ns"),
                ],
                data={"profile": [0.0, 1.0, -1.0, 1.0, 0.0]},
            ),
            mock.Mock(spec=TariffCharge, reset_period=ConsumptionResetPeriod.DAILY),
            datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")),
            mock.Mock(spec=TariffUnit, convention=SignConvention.Passive),
            [0.0, 0.0, 1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0, 1.0, 1.0],
            [0.0, 1.0, 1.0, 2.0, 2.0],
        ),
    ],
)
def test_meter_profile_schema_transform_method(
    data: pd.DataFrame,
    charge: TariffCharge,
    billing_start: datetime,
    meter_unit: TariffUnit,
    exp_import_profile: list[float],
    exp_export_profile: list[float],
    exp_cumsum_import: list[float],
    exp_cumsum_export: list[float],
) -> None:
    """TODO"""

    transformed = transform(data, charge, billing_start, meter_unit)

    assert list(transformed._import_profile) == exp_import_profile
    assert list(transformed._export_profile) == exp_export_profile
    assert list(transformed._import_profile_cumsum) == exp_cumsum_import
    assert list(transformed._export_profile_cumsum) == exp_cumsum_export
