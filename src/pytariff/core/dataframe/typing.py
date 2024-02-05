from typing import TypeVar
from pytariff.core.dataframe.cost import TariffCostSchema

from pytariff.core.dataframe.profile import MeterProfileSchema


TariffFrameSchema = TypeVar("TariffFrameSchema", MeterProfileSchema, TariffCostSchema)
