from typing import Any

from whenever import Time

from pytariff.time_period import TimePeriod


class TestTimePeriod:
    def test_time_period_construction(
        self, start_time: object, end_time: object, finite: bool, context: Any
    ) -> None:
        """Assert that it is possible to construct (only) valid instances of a TimePeriod, or otherwise
        that the appropriate Exception is raised"""

        with context:
            inst = TimePeriod(start_time, end_time, finite)
            assert inst.start_time == start_time and inst.end_time == end_time

    def test_time_period_membership(
        self, period: TimePeriod, candidate_time: Time, is_expected_member: bool
    ) -> None:
        """Assert that a given candidate time object is either in the period defined by the given Period if expected,
        or otherwise that it is not, if not expected"""

        assert (candidate_time in period) is is_expected_member

    def test_time_period_normalise_cases(
        self,
        start_time: Time,
        end_time: Time,
        finite: bool,
        expected_periods: list[TimePeriod],
    ) -> None:
        """Assert that we correctly normalise the given Period"""

        normed = TimePeriod(start_time, end_time, finite).normalise()

        for idx, np in enumerate(normed):
            assert expected_periods[idx] == np

    # def test_time_period_intersection(
    #     self,
    #     period_a: TimePeriod | object,
    #     period_b: TimePeriod | object,
    #     expected_intersection: TimePeriod | None,
    #     context: Any,
    # ) -> None:
    #     """Assert that the intersection between two valid TimePeriod instances is correctly calculated, or else that
    #     the intersection is None; assert that intersection between a TimePeriod and any other class raises the expected
    #     Exception subclass"""
    #     pass


# def time_to_minutes(time_str):
#     """Converts a time string 'HH:MM' to minutes since midnight."""
#     hours, minutes = map(int, time_str.split(":"))
#     return hours * 60 + minutes


# def intersect_periods(start1, end1, start2, end2):
#     """Finds the intersection of two time periods, considering potential wrap-around midnight."""

#     # Handle periods that span midnight (i.e., start > end)
#     def normalize_period(start_min, end_min):
#         if start_min > end_min:
#             # Split into two periods: one before midnight and one after midnight
#             return [(start_min, 1440), (0, end_min)]  # 1440 is 24 hours in minutes
#         else:
#             return [(start_min, end_min)]

#     # Normalize both periods
#     periods1 = normalize_period(start1, end1)
#     periods2 = normalize_period(start2, end2)

#     # Find the intersection of each segment
#     intersections = []
#     for p1_start, p1_end in periods1:
#         for p2_start, p2_end in periods2:
#             # Find the intersection of [p1_start, p1_end] and [p2_start, p2_end]
#             intersect_start = max(p1_start, p2_start)
#             intersect_end = min(p1_end, p2_end)

#             if intersect_start < intersect_end:
#                 intersections.append((intersect_start, intersect_end))

#     # Convert minutes back to 'HH:MM' format
#     def minutes_to_time(minutes):
#         return f"{minutes // 60:02}:{minutes % 60:02}"

#     # Format the intersections into time ranges
#     result = [
#         (minutes_to_time(start), minutes_to_time(end)) for start, end in intersections
#     ]

#     return result


# # Example usage:
# start1, end1 = "23:30", "02:00"  # Time period 1: 11:30 PM to 2:00 AM
# start2, end2 = "00:30", "03:00"  # Time period 2: 12:30 AM to 3:00 AM

# intersections = intersect_periods(start1, end1, start2, end2)

# print("Intersection periods:")
# for start, end in intersections:
#     print(f"{start} to {end}")
