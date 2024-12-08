from dataclasses import dataclass

from whenever import ZonedDateTime


@dataclass
class DefinedInterval:
    start: ZonedDateTime
    end: ZonedDateTime
