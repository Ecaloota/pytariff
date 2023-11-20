from typing import Generic

from utal.schema.applied_interval import AppliedInterval
from utal.schema.block import ConsumptionBlock, DemandBlock
from utal.schema.charge import BlockType, TariffCharge


class TariffInterval(AppliedInterval, Generic[BlockType]):
    """A TariffInterval is a right-open time interval over [start_time, end_time)
    associated with a single TariffCharge"""

    charge: TariffCharge[BlockType]


class ConsumptionInterval(TariffInterval[ConsumptionBlock]):
    pass


class DemandInterval(TariffInterval[DemandBlock]):
    pass
