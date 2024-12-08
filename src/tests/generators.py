import itertools
from contextlib import nullcontext
from dataclasses import dataclass
from itertools import permutations, product

import pytest

from pytariff.day import DayType
from tests.utils import RightOpenIntervalCases


@dataclass
class ParametrizedArgs:
    argnames: list[str]
    funcargs: list[tuple]


class Generators:
    # DayType Generators
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

        supercls_inter_disjoint = [
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

        supercls_inter_weekday_week_end = [
            (x, y, {}) for x, y in product(weekdays, [DayType.WEEKENDS])
        ] + [(y, x, {}) for x, y in product(weekdays, [DayType.WEEKENDS])]

        supercls_inter_weekend_week_end = [
            (x, y, {x}) for x, y in product(weekends, [DayType.WEEKENDS])
        ] + [(y, x, {x}) for x, y in product(weekends, [DayType.WEEKENDS])]

        supercls_inter_weekend_week_day = [
            (x, y, {}) for x, y in product(weekends, [DayType.WEEKDAYS])
        ] + [(y, x, {}) for x, y in product(weekends, [DayType.WEEKDAYS])]

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

    # TariffBlock Generators
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
