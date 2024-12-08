import pytest
from whenever import Time
from whenever_time_period import LinearTimePeriod

from pytariff.block import TariffBlock
from pytariff.day import DayType
from pytariff.interval import TariffInterval
from pytariff.rate import TariffRate


class TestTariffInterval:
    def test_tariff_interval_construction(self) -> None:
        TariffInterval(
            time_period=LinearTimePeriod(start_time=Time(1), end_time=Time(2)),
            days_applied=set([DayType.MONDAY]),
            blocks=[
                TariffBlock(from_quantity=0, to_quantity=1),
                TariffBlock(from_quantity=1, to_quantity=10),
            ],
            rates=[TariffRate("AUD", 1), TariffRate("AUD", 2)],
            trade_direction="Import",
            sign_convention="Passive",
            metric="Consumption",
        )

        with pytest.raises(ValueError):
            TariffInterval(
                time_period=LinearTimePeriod(start_time=Time(1), end_time=Time(2)),
                days_applied=set([DayType.MONDAY]),
                blocks=[
                    TariffBlock(from_quantity=0.5, to_quantity=10),
                    TariffBlock(from_quantity=0, to_quantity=1),
                ],
                rates=[TariffRate("AUD", 1), TariffRate("AUD", 2)],
                trade_direction="Import",
                sign_convention="Passive",
                metric="Consumption",
            )
