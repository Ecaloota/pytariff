from dataclasses import FrozenInstanceError
from typing import Any
from unittest.mock import Mock

import pytest

from pytariff.block import TariffBlock
from pytariff.rate import TariffRate
from tests.utils import IntervalIntersectionCase


class TestTariffBlock:
    def test_tariff_block_construction(
        self, from_quantity: float, to_quantity: float, context: Any
    ) -> None:
        """Given some valid `from_quantity` and `to_quantity` values, assert that
        it is possible to construct a valid TariffBlock instance, or otherwise
        that it is not possible with invalid values."""

        mock_rate = Mock(spec=TariffRate)

        with context:
            TariffBlock(
                rate=mock_rate, from_quantity=from_quantity, to_quantity=to_quantity
            )

    def test_tariff_block_intersection(self, case: IntervalIntersectionCase) -> None:
        """Given some IntervalIntersectionCase for right-closed intervals, assert
        that the intersection between the TariffBlock constructed from the Case-left
        and Case-right abides the expected intersection rules."""

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

    def test_tariff_block_ordering(
        self, case: IntervalIntersectionCase, expected_ordering: bool
    ) -> None:
        """Given some pair of TariffBlocks A and B, assert that the relative ordering of those Blocks
        abides the expected rule, specifically that A.from_quantity < B.from_quantity"""

        block_a = TariffBlock(from_quantity=case.left.left, to_quantity=case.left.right)
        block_b = TariffBlock(
            from_quantity=case.right.left, to_quantity=case.right.right
        )

        assert (block_a.from_quantity < block_b.from_quantity) is expected_ordering

    def test_tariff_block_immutability(self) -> None:
        """Given some TariffBlock, assert that attempting to mutate its values
        raises the expected FrozenInstanceError exception"""

        block = TariffBlock(from_quantity=5.0, to_quantity=10.0)

        with pytest.raises(FrozenInstanceError):
            block.from_quantity = 4.0

        with pytest.raises(FrozenInstanceError):
            block.to_quantity = 11.0
