from dataclasses import dataclass

# the intent is for this to handle user inputs (with some constraints) and transform those inputs
# into meter profiles which can be understood by pytariff. Specifically, it should take inputs and
# return information about the quantity and units of some usage profile.

# this could be a pandas dataframe, as we did last time. Or it could be a pair of numpy arrays.
# the issue will arise, as with last time, if we encounter non-uniform profile sampling, or
# if the reset periods or billing periods are not aligned with the profile.

# Note, I've decided that we don't actually need a profile to be sampled uniformly.
# The step size when simulating can just be the
# min(next_profile_step, next_tariff_rate_change / next_thing_change).


@dataclass
class ProfileHandler:
    pass
