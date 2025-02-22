from whenever import ZonedDateTime

from pytariff.profile import Profile
from pytariff.reset import ChargeMethod, ResetFrequency, ResetPeriod
from tests.synthetic_profiles import SYNTHETIC_PROFILE_B


def test_profile_transform() -> None:
    f = Profile(SYNTHETIC_PROFILE_B).transform(
        ResetPeriod(
            anchor=ZonedDateTime(2024, 1, 1, tz="UTC"),
            frequency=ResetFrequency._MINUTELY,
            charge_method=ChargeMethod._Infinity,
        )
    )
