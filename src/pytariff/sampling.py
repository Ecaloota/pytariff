from enum import Enum
from typing import Any, TypedDict

import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.linear_model import LinearRegression
from whenever import TimeDelta, ZonedDateTime

from pytariff.regressors import MovingAverageRegressor, PiecewiseConstantRegressor


class ResampleFrequency(TypedDict, total=False):
    """We define a sensible subset of allowed keys which can be used when
    passing kwargs to whenever's abstract add method in
    Profile.resample"""

    hours: float
    minutes: float
    seconds: float


class SamplingMethod(Enum):
    """Maps a SamplingMethod choice to the corresponding scikit-learn regressor"""

    GaussianProcessRegression = GaussianProcessRegressor
    LinearInterpolation = LinearRegression
    MovingAverage = MovingAverageRegressor
    PiecewiseConstant = PiecewiseConstantRegressor

    def __call__(
        cls,
        profile: dict[ZonedDateTime, float],
        sample_start: ZonedDateTime | None,
        sample_end: ZonedDateTime | None,
        frequency: ResampleFrequency,
        regressor_kwargs: dict[str, Any] = {},
    ) -> dict[ZonedDateTime, float]:
        """TODO"""

        if not sample_start:
            sample_start = min(profile.keys())
        if not sample_end:
            sample_end = max(profile.keys())

        # Generate the resampled keys
        keys: list[ZonedDateTime] = []
        N = 0
        while sample_start + N * TimeDelta(**frequency) <= sample_end:
            keys.append(sample_start + N * TimeDelta(**frequency))
            N += 1

        # Generate the (continuous) values over [start, end] using the chosen method
        # and sample the distribution at each k in sk_keys
        sk_prof_keys = np.array([x.timestamp() for x in profile.keys()]).reshape(-1, 1)
        sk_prof_vals = list(profile.values())
        sk_keys = np.array([k.timestamp() for k in keys]).reshape(-1, 1)
        y_pred = (
            cls.value(**regressor_kwargs)
            .fit(sk_prof_keys, sk_prof_vals)
            .predict(sk_keys)
        )

        return dict(zip(keys, y_pred))
