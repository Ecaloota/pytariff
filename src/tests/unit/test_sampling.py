from whenever import ZonedDateTime

from pytariff.profile import Profile
from pytariff.sampling import ResampleFrequency, SamplingMethod
from tests.synthetic_profiles import SYNTHETIC_PROFILE_A, SYNTHETIC_PROFILE_B


# TODO construct this test such that the answer becomes mathematically trivial to assert
# currently, we obtain a linear prediction which is not (clearly/trivially) correct
def test_sampling() -> None:
    f = Profile(SYNTHETIC_PROFILE_A).resample(
        start=ZonedDateTime(2024, 12, 29, tz="UTC"),
        end=ZonedDateTime(2025, 1, 3, tz="UTC"),
        method=SamplingMethod.MovingAverage,
        frequency=ResampleFrequency({"minutes": 10}),
        regressor_kwargs={"window_size": 100},
    )


# TODO these are placeholder/dev tests at best
def test_regressor() -> None:
    f = Profile(SYNTHETIC_PROFILE_B).resample(
        start=ZonedDateTime(2023, 12, 31, 23, 30, tz="UTC"),
        end=ZonedDateTime(2024, 1, 1, 0, 50, tz="UTC"),
        method=SamplingMethod.PiecewiseConstant,
        frequency=ResampleFrequency({"minutes": 5}),
    )
