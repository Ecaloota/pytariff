import operator
from abc import ABC
from typing import Literal

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


class MeanTransformer(AbstractTransformer):
    def transform(
        self,
        profile: dict[ZonedDateTime, float],
        transform_start: ZonedDateTime,
        transform_end: ZonedDateTime,
    ) -> dict[ZonedDateTime, float]:
        return {}


class MaxTransformer(AbstractTransformer):
    def transform(
        self,
        profile: dict[ZonedDateTime, float],
        transform_start: ZonedDateTime,
        transform_end: ZonedDateTime,
    ) -> dict[ZonedDateTime, float]:
        return {}


class RollingMaxTransformer(AbstractTransformer):
    def transform(
        self,
        profile: dict[ZonedDateTime, float],
        transform_start: ZonedDateTime,
        transform_end: ZonedDateTime,
    ) -> dict[ZonedDateTime, float]:
        return {}


class CumSumTransformer(AbstractTransformer):
    def transform(
        self,
        profile: dict[ZonedDateTime, float],
        transform_start: ZonedDateTime,
        transform_end: ZonedDateTime,
    ) -> dict[ZonedDateTime, float]:
        return {}
