from pytariff.reset import ResetFrequency


class TestReset:
    def test_reset_frequency_enum(self) -> None:
        """TODO"""
        # etc
        assert ResetFrequency.DAILY.name == "DAILY"
        assert ResetFrequency.DAILY == ResetFrequency("DAILY")
        assert ResetFrequency.DAILY.value == {"days": 1}

    def test_charge_method(self) -> None:
        """TODO"""
        pass

    # TODO test the next_reset generator specifically over normal and unintuitive DST
    # transitions. Assert that the way we are calling the current.add(**self.frequency.value)
    # is robust w.r.t. each of the ResetFrequency values.
    def test_reset_period(self) -> None:
        """TODO"""
        pass
