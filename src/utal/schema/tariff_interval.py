from utal.schema.applied_interval import AppliedInterval
from utal.schema.charge import TariffCharge


class TariffInterval(AppliedInterval):
    """A TariffInterval is a right-open time interval over [start_time, end_time)
    associated with a single TariffCharge"""

    charge: TariffCharge
