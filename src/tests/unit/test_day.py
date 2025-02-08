from pytariff.day import DayType


class TestDayType:
    def test_day_type_intersection(
        self,
        day_type_a: DayType,
        day_type_b: DayType,
        expected_intersection: set[DayType],
    ) -> None:
        """Given some pair of DayTypes, assert that their intersection abides
        the expected rules"""
        assert day_type_a & day_type_b == expected_intersection
