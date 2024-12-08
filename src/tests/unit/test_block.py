from typing import Any
from unittest.mock import Mock

from pytariff.block import TariffBlock
from pytariff.rate import TariffRate
from tests.utils import IntervalIntersectionCase


class TestTariffBlock:
    def test_tariff_block_construction(
        self, from_quantity: float, to_quantity: float, context: Any
    ) -> None:
        """TODO"""

        mock_rate = Mock(spec=TariffRate)

        with context:
            TariffBlock(
                rate=mock_rate, from_quantity=from_quantity, to_quantity=to_quantity
            )

    def test_tariff_block_intersection(self, case: IntervalIntersectionCase) -> None:
        """TODO"""

        block_a = TariffBlock(from_quantity=case.left.left, to_quantity=case.left.right)
        block_b = TariffBlock(
            from_quantity=case.right.left, to_quantity=case.right.right
        )

        if case.intersection:
            assert (block_a & block_b) == TariffBlock(
                from_quantity=case.intersection.left,
                to_quantity=case.intersection.right,
            )
        else:
            assert (block_a & block_b) is None
