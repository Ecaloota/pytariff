from typing import Any

import matplotlib.pyplot as plt
import seaborn as sns
from whenever import ZonedDateTime

from pytariff.reset import ResetPeriod
from pytariff.sampling import ResampleFrequency, SamplingMethod
from pytariff.unit import SignConvention


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

    def resample(
        self,
        start: ZonedDateTime,
        end: ZonedDateTime,
        method: SamplingMethod,
        frequency: ResampleFrequency,
        regressor_kwargs: dict[str, Any] = {},
    ) -> "Profile":
        """Resample the Profile (between start and end, inclusive) at the given ResampleFrequency
        using the provided SamplingMethod.
        """
        self.data = method(self.data, start, end, frequency, regressor_kwargs)
        return self

    # does it make sense to allow resampling following transformation? and vice-versa?
    def transform(self, reset_data: ResetPeriod) -> "Profile":
        """Transform the Profile using the given ResetPeriod."""
        self.data = reset_data.get_transformed_profile(self.data)
        return self

    def plot(self, **kwargs: dict[str, Any]) -> None:
        """Generate a plot of the Profile using Seaborn `lineplot`."""

        sns.lineplot(
            x=[_.py_datetime() for _ in self.data.keys()],
            y=[_ for _ in self.data.values()],
            **kwargs,
        )
        plt.show()
