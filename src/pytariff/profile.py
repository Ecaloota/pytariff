from whenever import ZonedDateTime

from pytariff.sampling import ResampleFrequency, SamplingMethod
from pytariff.unit import SignConvention

# the intent is for this to handle user inputs (with some constraints) and transform those inputs
# into meter profiles which can be understood by pytariff. Specifically, it should take inputs and
# return information about the quantity and units of some usage profile.

# this could be a pandas dataframe, as we did last time. Or it could be a pair of numpy arrays.
# the issue will arise, as with last time, if we encounter non-uniform profile sampling, or
# if the reset periods or billing periods are not aligned with the profile.

# Note, I've decided that we don't actually need a profile to be sampled uniformly.
# The step size when simulating can just be the
# min(next_profile_step, next_tariff_rate_change / next_thing_change).
# NOTE TO SELF: this is actually (only?) true if we use a piecewise-constant
# approximation


class Profile:
    """A Profile is an unordered association between a unique point in time and
    some quantity of power being transacted at that time.

    Example:

    >>> Profile(
        data={
            ZonedDateTime(2024, 1, 1, 0, 0, 0, tz="UTC"): 1.0,
            ZonedDateTime(2024, 1, 1, 0, 0, 5, tz="UTC"): 2.0,
            ZonedDateTime(2024, 1, 1, 0, 0, 15, tz="UTC"): -1.0,
            ZonedDateTime(2024, 1, 1, 0, 0, 11, tz="UTC"): 0.0,
        }
    )
    """

    def __init__(
        self,
        data: dict[ZonedDateTime, float],
        sign_convention: SignConvention = SignConvention.Passive,
    ) -> None:
        self._original_data = data
        self._data = data
        self.sign_convention = sign_convention

    @property
    def data(self) -> dict[ZonedDateTime, float]:
        return self._data

    @data.setter
    def data(self, other: dict[ZonedDateTime, float]) -> None:
        self._data = other

    # TODO
    # This function should basically just pass self.data to the functionality
    # provided by the sampling method and return a dict containing impulse-samples
    # at the start + resample_frequency * N while
    # start + resample_frequency * N <= end.
    def resample(
        self,
        start: ZonedDateTime,
        end: ZonedDateTime,
        method: SamplingMethod,
        frequency: ResampleFrequency,
    ) -> dict[ZonedDateTime, float]:
        return  # type: ignore  # TODO
