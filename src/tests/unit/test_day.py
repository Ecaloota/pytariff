from pytariff.day import DayType


class TestDayType:
    def test_day_type_intersection(
        self,
        day_type_a: DayType,
        day_type_b: DayType,
        expected_intersection: set[DayType],
    ):
        """TODO"""
        assert day_type_a & day_type_b == expected_intersection
