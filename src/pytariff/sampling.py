from enum import Enum
from typing import TypedDict


class ResampleFrequency(TypedDict, total=False):
    """We define a sensible subset of allowed keys which can be used when
    passing kwargs to whenever's abstract add method in
    Profile.resample"""

    days: int
    hours: float
    minutes: float
    seconds: float


# This is intended to be an Enum which defines the various ways we might sample
# a user profile. This is essentially discrete time series sampling, which is
# a deep rabbit hole. Options could include Gaussian Process Regression,
# linear or polynomial interpolation, moving average, and piecewise-constant approximation
# For all options (except optionally, PiecewiseConstant), we need to also select
# a resampled frequency, and we can then use the resampled data to compute
# tariff values.
class SamplingMethod(Enum):
    GaussianProcessRegression = "GPR"
    LinearInterpolation = "Linear"
    PolynomialInterpolation = "Polynomial"
    MovingAverage = "MovingAverage"
    PiecewiseConstant = "PiecewiseConstant"
