from enum import Enum


class TariffUnit(Enum):
    """Not to be used directly"""

    pass


class ConsumptionUnit(TariffUnit, Enum):
    kWh = "KWh"
    _null = "_null"  # for internal use only


class DemandUnit(TariffUnit, Enum):
    kW = "KW"
    _null = "_null"  # for internal use only


class RateCurrency(Enum):
    AUD = ("$", "AUD")
    _null = ("_null", "_null")  # for internal use only

    def __init__(self, symbol: str, iso: str) -> None:
        self._symbol = symbol
        self._iso = iso

    def __repr__(self) -> str:
        return self._iso + ":" + self._symbol

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def sign(self) -> str:
        return self._symbol

    @property
    def iso(self) -> str:
        return self._iso
