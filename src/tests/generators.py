import itertools
import random
from contextlib import nullcontext
from dataclasses import dataclass
from itertools import permutations, product

import pytest
from whenever import Time

from pytariff.day import DayType
from pytariff.time_period import TimePeriod
from tests.utils import TestUtils


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

    # TimePeriod Generators
    def time_period_construction_cases() -> ParametrizedArgs:
        """Generate relevant cases to assert that TimePeriod construction
        is valid given valid inputs, or otherwise that the appropriate exception is
        raised"""

        # relevant cases are:
        #   1. start_time < end_time
        #   2. start_time == end_time, finite
        #   3. start_time == end_time, infinite
        #   4. start_time != end_time, infinite (ValueError)
        #   5. start_time > end_time
        #   6. start_time is invalid type OR end_time is invalid type

        cases = [
            (Time(0), Time(1), True, nullcontext(None)),
            (Time(0), Time(0), True, nullcontext(None)),
            (Time(0), Time(0), False, nullcontext(None)),
            (Time(1), Time(0), True, nullcontext(None)),
            (Time(1), Time(0), False, pytest.raises(ValueError)),
            ("1", Time(0), True, pytest.raises(TypeError)),
            (Time(1), "0", True, pytest.raises(TypeError)),
        ]

        return ParametrizedArgs(
            argnames=["start_time", "end_time", "finite", "context"], funcargs=cases
        )

    def time_period_membership_cases() -> ParametrizedArgs:
        """Generate relevant cases to assert that a given Time is contained within
        the period defined by a TimePeriod"""

        start_int, end_int = TestUtils.generate_integers(2, 0, 23, min_gap=3)
        start_time, end_time = Time(start_int), Time(end_int)

        # given an interval [a, b) where a < b and b-a >= 3 and a,b in [0, 23],
        # some value C is in [a, b) when a <= C < b. (Cond. 1)
        # likewise, C is not in [a, b) when 0 <= C < a OR b <= C <= 23 (Cond. 2)
        member_candidate_a_lt_b = Time(
            random.randint(start_int, end_int - 1)
        )  # by Cond. 1
        non_member_a_lt_b = Time(
            random.choice(
                [
                    random.randint(0, start_int - 1),
                    random.randint(end_int, Time.MAX.hour),
                ]
                if start_int != 0
                else [random.randint(end_int, Time.MAX.hour)]
            )
        )  # by Cond. 2

        # given an interval [a, b) where b < a and (23-a)+b >= 3 and a,b in [0, 23],
        # some value C is in [a, b) when a <= C <= 23 AND 0 <= C < b (Cond. 3)
        # likewise, C is not in [a, b) when b <= C < a. (Cond. 4)
        member_candidate_a_gt_b = Time(
            random.choice(
                [
                    random.randint(end_int, Time.MAX.hour),
                    random.randint(0, start_int - 1),
                ]
                if start_int != 0
                else [random.randint(end_int, Time.MAX.hour)]
            )
        )  # by Cond. 3

        non_member_a_gt_b = Time(
            random.randint(start_int, end_int - 1)
        )  # by Cond. 4, end_int != 0

        cases = [
            (  # start_time < end_time and candidate time in period
                TimePeriod(start_time, end_time),
                member_candidate_a_lt_b,
                True,
            ),
            (  # start_time < end_time and !candidate time in period
                TimePeriod(start_time, end_time),
                non_member_a_lt_b,
                False,
            ),
            (  # start_time < end_time and c == start_time (True)
                TimePeriod(start_time, end_time),
                start_time,
                True,
            ),
            (  # start_time < end_time and c == end_time (False)
                TimePeriod(start_time, end_time),
                end_time,
                False,
            ),
            (  # start_time == end_time, period is infinite (all candidate times in period)
                TimePeriod(start_time, start_time, finite=False),
                end_time,
                True,
            ),
            (  # start_time == end_time, period is finite
                TimePeriod(start_time, start_time, finite=True),
                end_time,
                False,
            ),
            (  # start_time == end_time and c == start_time == end_time,
                # period is infinite (all candidate times in period)
                TimePeriod(start_time, start_time, finite=False),
                start_time,
                True,
            ),
            (  # start_time == end_time and c == start_time == end_time,
                # period is finite (candidate time equals instant covered by interval)
                TimePeriod(start_time, start_time, finite=False),
                start_time,
                True,
            ),
            (  # start_time > end_time and candidate_time in period
                TimePeriod(end_time, start_time),
                member_candidate_a_gt_b,
                True,
            ),
            (  # start_time > end_time and !c in period
                TimePeriod(end_time, start_time),
                non_member_a_gt_b,
                False,
            ),
            (  # start_time > end_time and c == start_time (False)
                TimePeriod(end_time, start_time),
                start_time,
                False,
            ),
            (  # start_time > end_time and c == end_time (True)
                TimePeriod(end_time, start_time),
                end_time,
                True,
            ),
        ]

        return ParametrizedArgs(
            argnames=["period", "candidate_time", "is_expected_member"], funcargs=cases
        )

    def time_period_normalise_cases() -> ParametrizedArgs:
        """Generate relevant cases to ensure we correctly normalise all instances of
        TimePeriod;

        Relevant cases are:
        1. start_time < end_time
        2. start_time == end_time, finite
        3. start_time == end_time, infinite
        4. start_time > end_time
        5. start_time == Time.MAX
        6. end_time == Time.MIDNIGHT
        7. start_time == Time.MAX && end_time == Time.MIDNIGHT
        """

        cases = [
            (Time(5), Time(10), True, [TimePeriod(Time(5), Time(10))]),
            (
                Time(10),
                Time(5),
                True,
                [TimePeriod(Time.MIDNIGHT, Time(5)), TimePeriod(Time(10), Time.MAX)],
            ),
            (
                Time(10),
                Time(10),
                False,
                [TimePeriod(Time.MIDNIGHT, Time.MIDNIGHT, finite=False)],
            ),
            (
                Time.MAX,
                Time(5),
                True,
                [TimePeriod(Time.MIDNIGHT, Time(5)), TimePeriod(Time.MAX, Time.MAX)],
            ),
            (
                Time(5),
                Time.MIDNIGHT,
                True,
                [
                    TimePeriod(Time.MIDNIGHT, Time.MIDNIGHT),
                    TimePeriod(Time(5), Time.MAX),
                ],
            ),
            (
                Time.MAX,
                Time.MIDNIGHT,
                True,
                [
                    TimePeriod(Time.MIDNIGHT, Time.MIDNIGHT),
                    TimePeriod(Time.MAX, Time.MAX),
                ],
            ),
        ]

        return ParametrizedArgs(
            argnames=["start_time", "end_time", "finite", "expected_periods"],
            funcargs=cases,
        )
