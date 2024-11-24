from dataclasses import dataclass
from typing import Optional

from whenever import Time

## PART OF REFACTOR -> TODO


@dataclass
class TimePeriod:
    """A TimePeriod is a right-open clock interval of whenever.Time objects,
    [start_time, end_time). The following are valid examples of TimePeriod objects,
    which may wrap around midnight.

    Examples:
    >> TimePeriod(start_time=Time(6), end_time=Time(18))
    >> TimePeriod(start_time=Time(18), end_time=Time(6))
    >> TimePeriod(start_time(5), end_time(5))  # covers only the instant at Time(5)
    >> TimePeriod(start_time(5), end_time(5), finite=False)  # implies infinite interval, covers all clock time
    """

    start_time: Time
    end_time: Time
    finite: bool = True

    def __post_init__(self):
        if not isinstance(self.start_time, Time) or not isinstance(self.end_time, Time):
            raise TypeError

        # if infinite interval, start_time == end_time
        if not self.finite and self.start_time != self.end_time:
            raise ValueError

    def __contains__(self, other: object) -> bool:
        if not isinstance(other, Time):
            raise TypeError

        if self.start_time <= self.end_time:
            # if self is infinite with start_time == end_time, other is contained in self
            if self.start_time == self.end_time and not self.finite:
                return True
            # if self is finite with start_time == end_time, other is contained in self
            # iff other == self.start_time (e.g. equals the instant described by self)
            elif self.start_time == self.end_time:
                return self.start_time == other
            return self.start_time <= other < self.end_time
        return self.start_time <= other or other < self.end_time

    def __and__(self, other: object) -> Optional["TimePeriod"]:
        if not isinstance(other, TimePeriod):
            raise TypeError

        start_inter = max(self.start_time, other.start_time)
        end_inter = min(self.end_time, other.end_time)

        # there is an edge condition here I think when start_inter < end_inter?
        return TimePeriod(start_time=start_inter, end_time=end_inter)

    # to order list[TimePeriod]
    def __lt__(self, other: "TimePeriod") -> bool:
        return self.start_time < other.start_time

    def normalise(self) -> list["TimePeriod"]:
        """Normalise a TimePeriod into constituent TimePeriod(s) such that each period
        has start_time < end_time. Calling normalise on an infinite interval returns the
        infinite interval centered at Time.MIDNIGHT.

        For example:
        # start_time < end_time
        >> TimePeriod(Time(5), Time(10)).normalise()
        >> [TimePeriod(Time(5), Time(10))]

        # start_time >= end_time, finite=True
        >> TimePeriod(Time(10), Time(5)).normalise()
        >> [TimePeriod(Time.MIDNIGHT, Time(5)), TimePeriod(Time(10), Time.MAX)]

        # start_time == end_time, finite=False
        >> TimePeriod(Time(10), Time(10), finite=False)
        >> [TimePeriod(Time.MIDNIGHT, Time.MIDNIGHT, finite=False)]

        # special case: start_time == Time.MAX
        >> TimePeriod(Time.MAX, Time(5)).normalise()
        >> [TimePeriod(Time.MIDNIGHT, Time(5)), TimePeriod(Time.MAX, Time.MAX)]

        # special case: end_time == Time.MIDNIGHT
        >> TimePeriod(Time(5), Time.MIDNIGHT).normalise()
        >> [TimePeriod(Time.MIDNIGHT, Time.MIDNIGHT), TimePeriod(Time(5), Time.MAX)]

        # special case: start_time == Time.MAX and end_time == Time.MIDNIGHT
        >> TimePeriod(Time.MAX, Time.MIDNIGHT).normalise()
        >> [TimePeriod(Time.MIDNIGHT, Time.MIDNIGHT), TimePeriod(Time.MAX, Time.MAX)]
        """

        if not self.finite:
            return [TimePeriod(Time.MIDNIGHT, Time.MIDNIGHT, finite=False)]

        p1 = TimePeriod(Time.MAX, Time.MAX) if self.start_time == Time.MAX else None
        p2 = (
            TimePeriod(Time.MIDNIGHT, Time.MIDNIGHT)
            if self.end_time == Time.MIDNIGHT
            else None
        )

        if self.start_time >= self.end_time:
            p1 = p1 if p1 else TimePeriod(self.start_time, Time.MAX)
            p2 = p2 if p2 else TimePeriod(Time.MIDNIGHT, self.end_time)
            return sorted([p1, p2])

        return [TimePeriod(self.start_time, self.end_time)]
