"""Contains synthetic user profiles, intended to be used during testing and development"""

from whenever import TimeDelta, ZonedDateTime

# Idealised profile
# One full day of usage data, 0 everywhere except between 100 and 150 (inclusive), else 1.
SYNTHETIC_PROFILE_A = {
    ZonedDateTime(2025, 1, 1, tz="UTC") + N * TimeDelta(minutes=5): 1
    if 100 <= N <= 150
    else 0
    for N in range(24 * 12 + 1)
}

SYNTHETIC_PROFILE_B = {
    ZonedDateTime(2024, 1, 1, tz="UTC"): 0,
    ZonedDateTime(2024, 1, 1, 0, 5, tz="UTC"): 2,
    ZonedDateTime(2024, 1, 1, 0, 10, tz="UTC"): 5,
    ZonedDateTime(2024, 1, 1, 0, 20, tz="UTC"): 0,
}
