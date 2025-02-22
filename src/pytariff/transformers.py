import operator
from abc import ABC
from typing import Literal

from scipy.ndimage import maximum_filter1d
from whenever import ZonedDateTime


class AbstractTransformer(ABC):
    def __init__(self, right: Literal["inclusive", "exclusive"] = "inclusive"):
        self.right_operator = operator.le if right == "inclusive" else operator.lt
        super().__init__()

    def transform(
        self,
        profile: dict[ZonedDateTime, float],
        transform_start: ZonedDateTime,
        transform_end: ZonedDateTime,
    ) -> dict[ZonedDateTime, float]:
        raise NotImplementedError


class IdentityTransformer(AbstractTransformer):
    def transform(
        self,
        profile: dict[ZonedDateTime, float],
        transform_start: ZonedDateTime,
        transform_end: ZonedDateTime,
    ) -> dict[ZonedDateTime, float]:
        return {
            k: profile[k]
            for k in profile.keys()
            if k >= transform_start and self.right_operator(k, transform_end)
        }


# this transformer is not intended for public use
class _InfiniteTransformer(AbstractTransformer):
    def transform(
        self,
        profile: dict[ZonedDateTime, float],
        transform_start: ZonedDateTime,
        transform_end: ZonedDateTime,
    ) -> dict[ZonedDateTime, float]:
        return {
            k: float("inf")
            for k in profile.keys()
            if k >= transform_start and self.right_operator(k, transform_end)
        }


class MeanTransformer(AbstractTransformer):
    def transform(
        self,
        profile: dict[ZonedDateTime, float],
        transform_start: ZonedDateTime,
        transform_end: ZonedDateTime,
    ) -> dict[ZonedDateTime, float]:
        return {
            k: sum(
                profile[k]
                for k in profile.keys()
                if k >= transform_start and self.right_operator(k, transform_end)
            )
            / len(profile.keys())
            for k in profile.keys()
            if k >= transform_start and self.right_operator(k, transform_end)
        }


class MaxTransformer(AbstractTransformer):
    def transform(
        self,
        profile: dict[ZonedDateTime, float],
        transform_start: ZonedDateTime,
        transform_end: ZonedDateTime,
    ) -> dict[ZonedDateTime, float]:
        return {
            k: max(
                profile[k]
                for k in profile.keys()
                if k >= transform_start and self.right_operator(k, transform_end)
            )
            for k in profile.keys()
            if k >= transform_start and self.right_operator(k, transform_end)
        }


# Note that we use an int window size here, but we could also use a ZonedDateTime window size
# to allow for more complex rolling windows when the profile does not have a constant frequency
class RollingMaxTransformer(AbstractTransformer):
    def transform(
        self,
        profile: dict[ZonedDateTime, float],
        transform_start: ZonedDateTime,
        transform_end: ZonedDateTime,
        window: int = 1,
    ) -> dict[ZonedDateTime, float]:
        # TODO explain in docs that we are using a rolling window with mode=nearest, such that
        # the array is padded with the nearest value when the window extends beyond the array edges
        rolling_max = maximum_filter1d(
            [
                v
                for k, v in profile.items()
                if k >= transform_start and self.right_operator(k, transform_end)
            ],
            size=window,
            mode="nearest",
        ).tolist()

        return dict(zip(profile.keys(), rolling_max))


class CumSumTransformer(AbstractTransformer):
    def transform(
        self,
        profile: dict[ZonedDateTime, float],
        transform_start: ZonedDateTime,
        transform_end: ZonedDateTime,
    ) -> dict[ZonedDateTime, float]:
        raise NotImplementedError
