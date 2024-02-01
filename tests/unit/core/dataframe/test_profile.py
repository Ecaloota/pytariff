from datetime import datetime
from unittest import mock
from zoneinfo import ZoneInfo
import pandas as pd
import numpy as np
import pytest
from pandera.errors import SchemaError
from utal.core.charge import TariffCharge


from utal.core.dataframe.profile import MeterProfileHandler, MeterProfileSchema
from utal.core.reset import ResetData, ResetPeriod
from utal.core.typing import Consumption
from utal.core.unit import SignConvention, TariffUnit, TradeDirection


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
    "data, charge_resolution, expected_resampled_list, raises",
    [
        (
            pd.DataFrame(
                index=[
                    pd.Timestamp(year=2023, month=1, day=1, hour=0, minute=0, tzinfo=ZoneInfo("UTC"), unit="ns"),
                    pd.Timestamp(year=2023, month=1, day=1, hour=0, minute=1, tzinfo=ZoneInfo("UTC"), unit="ns"),
                ],
                data={"profile": [0.0, 1.0]},
            ),
            "5min",
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
            "5min",
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
            "1min",
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
            "5min",
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
            "5min",
            [4.0, 2.0, -10.0],
            False,
        ),
    ],
)
def test_meter_profile_schema_resample_method(
    data: pd.DataFrame, charge_resolution: str, expected_resampled_list: list[float], raises: bool
) -> None:
    """TODO"""

    handler = MeterProfileHandler(data)
    resampled = handler._utal_resample(charge_resolution)
    assert list(resampled.profile) == expected_resampled_list


@pytest.mark.parametrize(
    "data, charge, exp_import_profile, exp_export_profile, exp_cumsum_import, exp_cumsum_export, exp_import_max, exp_export_max",  # noqa
    [
        (  # check basic usage; assert that import and export profiles are given the appropriate sign
            # and that the cumulative profiles are being calculated correctly
            pd.DataFrame(
                index=pd.date_range(
                    start="2023-01-01T00:00:00",
                    end="2023-01-01T00:05:00",
                    tz=ZoneInfo("UTC"),
                    freq="1min",
                    inclusive="left",
                ),
                data={"profile": [0.0, 1.0, -1.0, 1.0, 0.0]},
            ),
            mock.Mock(
                spec=TariffCharge,
                reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
                unit=TariffUnit(
                    metric=Consumption.kWh, direction=TradeDirection._null, convention=SignConvention.Passive
                ),
            ),
            [0.0, 0.0, 1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0, 1.0, 1.0],
            [0.0, 1.0, 1.0, 2.0, 2.0],
            [1.0, 1.0, 1.0, 1.0, 1.0],
            [1.0, 1.0, 1.0, 1.0, 1.0],
        ),
        (  # verify that the cumulative profiles are reset according to the provided reset_period
            pd.DataFrame(
                index=pd.date_range(
                    start="2023-01-01T00:00:00",
                    end="2023-01-04T00:00:00",
                    tz=ZoneInfo("UTC"),
                    freq="1h",
                    inclusive="left",
                ),
                data={"profile": np.tile(np.array([0.0] * 8 + [1.0] * 8 + [-1.0] * 8), 3)},
            ),
            mock.Mock(
                spec=TariffCharge,
                reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
                unit=TariffUnit(
                    metric=Consumption.kWh, direction=TradeDirection._null, convention=SignConvention.Passive
                ),
            ),
            list(np.tile(np.array([0.0] * 8 + [0.0] * 8 + [1.0] * 8), 3)),
            list(np.tile(np.array([0.0] * 8 + [1.0] * 8 + [0.0] * 8), 3)),
            list(np.tile(np.array([0.0] * 8 + [0.0] * 8 + list(np.arange(1, 9))), 3)),
            list(np.tile(np.array([0.0] * 8 + list(np.arange(1, 9)) + [8.0] * 8), 3)),
            list(np.array([1.0] * 72)),
            list(np.array([1.0] * 72)),
        ),
        (  # verify that the import and export columns are switched relative to the
            # first example when the SignConvention of the MeterProfile is set to Active
            pd.DataFrame(
                index=pd.date_range(
                    start="2023-01-01T00:00:00",
                    end="2023-01-01T00:05:00",
                    tz=ZoneInfo("UTC"),
                    freq="1min",
                    inclusive="left",
                ),
                data={"profile": [0.0, 1.0, -1.0, 1.0, 0.0]},
            ),
            mock.Mock(
                spec=TariffCharge,
                reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
                unit=TariffUnit(
                    metric=Consumption.kWh, direction=TradeDirection._null, convention=SignConvention.Active
                ),
            ),
            [0.0, 1.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0, 0.0, 0.0],
            [0.0, 1.0, 1.0, 2.0, 2.0],
            [0.0, 0.0, 1.0, 1.0, 1.0],
            [1.0, 1.0, 1.0, 1.0, 1.0],
            [1.0, 1.0, 1.0, 1.0, 1.0],
        ),
        (  # verify that the import and export max columns are calculated correctly
            pd.DataFrame(
                index=pd.date_range(
                    start="2023-01-01T00:00:00",
                    end="2023-01-04T00:00:00",
                    tz=ZoneInfo("UTC"),
                    freq="1h",
                    inclusive="left",
                ),
                data={"profile": np.tile(np.array([0.0] * 8 + [5.0] * 8 + [-1.0] * 8), 3)},
            ),
            mock.Mock(
                spec=TariffCharge,
                reset_data=ResetData(anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), period=ResetPeriod.DAILY),
                unit=TariffUnit(
                    metric=Consumption.kWh, direction=TradeDirection._null, convention=SignConvention.Passive
                ),
            ),
            list(np.tile(np.array([0.0] * 8 + [0.0] * 8 + [1.0] * 8), 3)),
            list(np.tile(np.array([0.0] * 8 + [5.0] * 8 + [0.0] * 8), 3)),
            list(np.tile(np.array([0.0] * 8 + [0.0] * 8 + list(np.arange(1, 9))), 3)),
            list(np.tile(np.array([0.0] * 8 + list(np.arange(5, 45, 5)) + [40.0] * 8), 3)),
            list(np.array([1.0] * 72)),
            list(np.array([5.0] * 72)),
        ),
    ],
)
def test_meter_profile_schema_transform_method(
    data: pd.DataFrame,
    charge: TariffCharge,
    exp_import_profile: list[float],
    exp_export_profile: list[float],
    exp_cumsum_import: list[float],
    exp_cumsum_export: list[float],
    exp_import_max: list[float],
    exp_export_max: list[float],
) -> None:
    """TODO"""

    handler = MeterProfileHandler(data)
    transformed = handler._utal_transform(datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")), charge)

    assert list(transformed._import_profile_usage) == exp_import_profile
    assert list(transformed._export_profile_usage) == exp_export_profile
    assert list(transformed._import_profile_usage_cumsum) == exp_cumsum_import
    assert list(transformed._export_profile_usage_cumsum) == exp_cumsum_export
    assert list(transformed._import_profile_usage_max) == exp_import_max
    assert list(transformed._export_profile_usage_max) == exp_export_max
