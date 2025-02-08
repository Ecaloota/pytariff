from __future__ import annotations

from dataclasses import dataclass

from whenever import ZonedDateTime


@dataclass
class DefinedInterval:
    start: ZonedDateTime
    end: ZonedDateTime

    def __post_init__(self) -> None:
        if self.start >= self.end:
            raise ValueError

    def __and__(self, other: DefinedInterval) -> DefinedInterval | None:
        start_inter = max(self.start, other.start)
        end_inter = min(self.end, other.end)

        if start_inter <= end_inter:
            return DefinedInterval(start=start_inter, end=end_inter)
        return None
