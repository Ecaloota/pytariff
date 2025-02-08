from typing import Any

from whenever import ZonedDateTime

from pytariff.defined_interval import DefinedInterval
from tests.generators import ParametrizedArgs


class TestDefinedInterval:
    def test_defined_interval_construction(
        self, start: ZonedDateTime, end: ZonedDateTime, context: Any
    ) -> ParametrizedArgs:
        """Given valid values for a DefinedInterval, assert that we can instantiate
        the corresponding DefinedInterval; given invalid values, assert that we raise
        a ValueError"""

        with context:
            assert DefinedInterval(start=start, end=end)

    def test_defined_interval_intersection(self) -> ParametrizedArgs:
        # TODO test of intersection, asserting we calculate the correct intersection
        # between two closed ZonedDateTime intervals
        pass
