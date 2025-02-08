import itertools
from contextlib import nullcontext
from dataclasses import dataclass
from itertools import permutations, product
from typing import Any

import pytest
from whenever import ZonedDateTime

from pytariff.day import DayType
from tests.utils import RightOpenIntervalCases


@dataclass
class ParametrizedArgs:
    argnames: list[str]
    funcargs: list[tuple]


class DayTypeGenerators:
    """Generators responsible for generating test cases over the DayType class"""

    @staticmethod
    def day_type_intersection_cases() -> ParametrizedArgs:
        """TODO"""

        weekdays = [
            DayType.MONDAY,
            DayType.TUESDAY,
            DayType.WEDNESDAY,
            DayType.THURSDAY,
            DayType.FRIDAY,
        ]
        weekends = [DayType.SATURDAY, DayType.SUNDAY]

        supercls_inter_identity = [(a, a, {a}) for a in DayType._member_map_.values()]

        supercls_inter_disjoint: list[tuple[DayType, DayType, dict[Any, Any]]] = [
            (a, b, {}) for a, b in permutations(weekdays + weekends, 2) if a != b
        ]

        supercls_inter_day_all_day = [
            (x, y, {x})
            for x, y in product(
                weekdays + weekends + [DayType.WEEKDAYS, DayType.WEEKENDS],
                [DayType.ALL_DAYS],
            )
        ] + [
            (y, x, {x})
            for x, y in product(
                weekdays + weekends + [DayType.WEEKDAYS, DayType.WEEKENDS],
                [DayType.ALL_DAYS],
            )
        ]

        supercls_inter_weekday_week_day = [
            (x, y, {x}) for x, y in product(weekdays, [DayType.WEEKDAYS])
        ] + [(y, x, {x}) for x, y in product(weekdays, [DayType.WEEKDAYS])]

        supercls_inter_weekday_week_end: list[
            tuple[DayType, DayType, dict[Any, Any]]
        ] = [(x, y, {}) for x, y in product(weekdays, [DayType.WEEKENDS])] + [
            (y, x, {}) for x, y in product(weekdays, [DayType.WEEKENDS])
        ]

        supercls_inter_weekend_week_end = [
            (x, y, {x}) for x, y in product(weekends, [DayType.WEEKENDS])
        ] + [(y, x, {x}) for x, y in product(weekends, [DayType.WEEKENDS])]

        supercls_inter_weekend_week_day: list[
            tuple[DayType, DayType, dict[Any, Any]]
        ] = [(x, y, {}) for x, y in product(weekends, [DayType.WEEKDAYS])] + [
            (y, x, {}) for x, y in product(weekends, [DayType.WEEKDAYS])
        ]

        return ParametrizedArgs(
            argnames=["day_type_a", "day_type_b", "expected_intersection"],
            funcargs=list(
                itertools.chain(
                    supercls_inter_identity,
                    supercls_inter_day_all_day,
                    supercls_inter_disjoint,
                    supercls_inter_weekday_week_day,
                    supercls_inter_weekday_week_end,
                    supercls_inter_weekend_week_end,
                    supercls_inter_weekend_week_day,
                )
            ),
        )


class TariffBlockGenerators:
    """Generators responsible for generating test cases over the TariffBlock class"""

    @staticmethod
    def tariff_block_cases() -> ParametrizedArgs:
        """Generate relevant cases for TariffBlock bounds (these are general wrt
        strictly positive right-open intervals); these cases are:
        1. from_quantity < to_quantity; from_quantity > 0, to_quantity > 0
        2. from_quantity > to_quantity; from_quantity > 0, to_quantity > 0
        3. from_quantity = to_quantity; from_quantity > 0, to_quantity > 0

        4. from_quantity < to_quantity; from_quantity < 0, to_quantity < 0
        5. from_quantity > to_quantity; from_quantity < 0, to_quantity < 0
        6. from_quantity = to_quantity; from_quantity < 0, to_quantity < 0

        7. from_quantity < to_quantity; from_quantity < 0, to_quantity > 0
        8. from_quantity > to_quantity; from_quantity > 0, to_quantity < 0

        9. from_quantity = to_quantity; from_quantity = 0, to_quantity = 0
        10. from_quantity = to_quantity; from_quantity = 0, to_quantity = float("inf")
        """

        a_lt_0, a_gt_0 = -5.0, 5.0
        b_lt_0, b_gt_0 = -4.0, 6.0

        cases = [
            (a_gt_0, b_gt_0, nullcontext()),  # 1
            (b_gt_0, a_gt_0, pytest.raises(ValueError)),  # 2
            (a_gt_0, a_gt_0, pytest.raises(ValueError)),  # 3
            (a_lt_0, b_lt_0, pytest.raises(ValueError)),  # 4
            (b_lt_0, a_lt_0, pytest.raises(ValueError)),  # 5
            (a_lt_0, a_lt_0, pytest.raises(ValueError)),  # 6
            (a_lt_0, a_gt_0, pytest.raises(ValueError)),  # 7
            (a_gt_0, a_lt_0, pytest.raises(ValueError)),  # 8
            (0, 0, pytest.raises(ValueError)),  # 9
            (0, float("inf"), nullcontext()),  # 10
        ]

        return ParametrizedArgs(
            argnames=["from_quantity", "to_quantity", "context"], funcargs=cases
        )

    @staticmethod
    def tariff_block_intersections() -> ParametrizedArgs:
        """TODO"""

        return ParametrizedArgs(
            argnames=["case"],
            funcargs=[
                (RightOpenIntervalCases.left_touching(),),
                (RightOpenIntervalCases.right_touching(),),
                (RightOpenIntervalCases.left_overlap(),),
                (RightOpenIntervalCases.right_overlap(),),
                (RightOpenIntervalCases.null_overlap(),),
                (RightOpenIntervalCases.complete_overlap(),),
                (RightOpenIntervalCases.complete_overlap_inf_edge_case(),),
            ],
        )

    @staticmethod
    def tariff_block_ordering_cases() -> ParametrizedArgs:
        """Generate the relevant cases required to demonstrate that the ordering of a pair of TariffBlocks
        abides by the expected rule"""

        return ParametrizedArgs(
            argnames=["case", "expected_ordering"],
            funcargs=[
                (RightOpenIntervalCases.left_touching(), True),
                (RightOpenIntervalCases.right_touching(), False),
                (RightOpenIntervalCases.left_overlap(), True),
                (RightOpenIntervalCases.right_overlap(), False),
                (RightOpenIntervalCases.null_overlap(), True),
                (RightOpenIntervalCases.complete_overlap(), False),
                (RightOpenIntervalCases.complete_overlap_inf_edge_case(), False),
            ],
        )


class DefinedIntervalGenerators:
    """Generators responsible for generating test cases over the DefinedInterval class"""

    @staticmethod
    def defined_interval_construction_cases() -> ParametrizedArgs:
        """Relevant cases are:

        1. start < end
        2. start = end (ValueError)
        3. start > end (ValueError)
        """

        return ParametrizedArgs(
            argnames=["start", "end", "context"],
            funcargs=[
                (
                    ZonedDateTime(
                        year=2023, month=1, day=1, hour=12, tz="Australia/Brisbane"
                    ),
                    ZonedDateTime(
                        year=2024, month=1, day=1, hour=12, tz="Australia/Brisbane"
                    ),
                    nullcontext(),
                ),
                (
                    ZonedDateTime(
                        year=2023, month=1, day=1, hour=12, tz="Australia/Brisbane"
                    ),
                    ZonedDateTime(
                        year=2023, month=1, day=1, hour=12, tz="Australia/Brisbane"
                    ),
                    pytest.raises(ValueError),
                ),
                (
                    ZonedDateTime(
                        year=2024, month=1, day=1, hour=12, tz="Australia/Brisbane"
                    ),
                    ZonedDateTime(
                        year=2023, month=1, day=1, hour=12, tz="Australia/Brisbane"
                    ),
                    pytest.raises(ValueError),
                ),
            ],
        )


class TariffRateGenerators:
    @staticmethod
    def tariff_rate_get_value_cases() -> ParametrizedArgs:
        """Assert that the .get_value() method of TariffRate works as expected"""

        cases = [(1.0, (None,), 1.0), (lambda x, y: x**y, (2, 3), 8.0)]
        return ParametrizedArgs(
            argnames=["value", "vargs", "expected_return"], funcargs=cases
        )
