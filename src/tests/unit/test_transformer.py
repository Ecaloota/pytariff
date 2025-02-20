from pytariff.transformers import IdentityTransformer
from tests.synthetic_profiles import SYNTHETIC_PROFILE_B


def test_transformer() -> None:
    # TODO implement this test properly

    transformed = IdentityTransformer(right="inclusive").transform(
        SYNTHETIC_PROFILE_B,
        min(SYNTHETIC_PROFILE_B.keys()),
        max(SYNTHETIC_PROFILE_B.keys()),
    )
