import random
from dataclasses import dataclass
from enum import StrEnum


class TestUtils:
    """A collection of test generator tools, (which themselves are tested)"""

    @staticmethod
    def generate_integers(
        N: int,
        min_val: int = 0,
        max_val: int = 23,
        min_gap: int = 1,
        max_gap: int = 10,
        _depth: int = 0,
        _max_retry: int = 10,
    ) -> list[int]:
        """Generates N distinct random integers in the given range [min_val, max_val]
        with a gap of at least min_gap and at most max_gap between each number."""

        required_range = N + (N - 1) * min_gap
        if required_range > (max_val - min_val + 1):
            raise ValueError

        numbers = []
        current = random.randint(min_val, max_val)
        numbers.append(current)

        while len(numbers) < N:
            min_possible = current + min_gap
            max_possible = current + max_gap

            if min_possible > max_possible or max_possible > max_val:
                _depth += 1
                if _depth > _max_retry:
                    raise ValueError
                return TestUtils.generate_integers(
                    N, min_val, max_val, min_gap, max_gap, _depth
                )

            next = random.randint(min_possible, max_possible)
            numbers.append(next)
            current = next

        return sorted(numbers)

    @staticmethod
    def get_str_enum_members(enum_type: StrEnum) -> list[str]:
        return [_ for _ in enum_type.__members__.keys()]


@dataclass
class Point:
    left: float
    right: float


@dataclass
class IntervalIntersectionCase:
    left: Point
    right: Point
    intersection: Point | None


class RightOpenIntervalCases:
    @staticmethod
    def left_touching() -> IntervalIntersectionCase:
        """
        [-----)
              [-----)
        """
        return IntervalIntersectionCase(Point(0, 100), Point(100, 200), None)

    @staticmethod
    def right_touching() -> IntervalIntersectionCase:
        """
              [-----)
        [-----)
        """
        return IntervalIntersectionCase(Point(100, 200), Point(0, 100), None)

    @staticmethod
    def left_overlap() -> IntervalIntersectionCase:
        """
        [-----)
            [-----)
        """
        return IntervalIntersectionCase(Point(0, 100), Point(50, 150), Point(50, 100))

    @staticmethod
    def right_overlap() -> IntervalIntersectionCase:
        """
            [-----)
        [-----)
        """
        return IntervalIntersectionCase(Point(50, 150), Point(0, 100), Point(50, 100))

    @staticmethod
    def null_overlap() -> IntervalIntersectionCase:
        """
        [-----)
                 [-----)
        """
        return IntervalIntersectionCase(Point(0, 50), Point(100, 150), None)

    @staticmethod
    def complete_overlap() -> IntervalIntersectionCase:
        """
        [-----)
        [-----)
        """
        return IntervalIntersectionCase(Point(0, 10), Point(0, 10), Point(0, 10))

    @staticmethod
    def complete_overlap_inf_edge_case() -> IntervalIntersectionCase:
        """As in complete_overlap with each Point .right = float("inf")"""
        return IntervalIntersectionCase(
            Point(0, float("inf")), Point(0, float("inf")), Point(0, float("inf"))
        )
