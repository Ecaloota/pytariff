from typing import Optional

from utal.schema.defined_interval import DefinedInterval
from utal.schema.tariff_interval import TariffInterval


class GenericTariff(DefinedInterval):
    """A GenericTariff is a closed datetime interval from [start, end]"""

    children: Optional[tuple[TariffInterval, ...]] = None
