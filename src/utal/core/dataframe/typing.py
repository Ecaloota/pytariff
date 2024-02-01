from typing import TypeVar
from utal.core.dataframe.cost import TariffCostSchema

from utal.core.dataframe.profile import MeterProfileSchema


TariffFrameSchema = TypeVar("TariffFrameSchema", MeterProfileSchema, TariffCostSchema)
