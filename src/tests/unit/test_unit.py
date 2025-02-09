from pytariff.unit import Metric, SignConvention, TradeDirection


class TestUnits:
    def test_trade_direction_enum(self) -> None:
        """Assert that the TradeDirection Enum behaves as expected"""
        assert TradeDirection.Import == TradeDirection("Import")
        assert TradeDirection.Import != TradeDirection("Export")
        assert TradeDirection.Export == TradeDirection("Export")

    def test_metric_enum(self) -> None:
        """Assert that the Metric Enum behaves as expected"""
        assert Metric.Consumption == Metric("Consumption")
        assert Metric.Consumption != Metric("Demand")
        assert Metric.Demand == Metric("Demand")

    def test_sign_convention_enum(self) -> None:
        """Assert that the SignConvention Enum behaves as expected"""

        # a bit cumbersome
        assert SignConvention.Passive == SignConvention("Passive")
        assert SignConvention.Passive != SignConvention("Active")
        assert SignConvention.Active == SignConvention("Active")

        assert SignConvention.Passive.import_factor == -1
        assert SignConvention.Passive.export_factor == 1

        assert SignConvention.Active.import_factor == 1
        assert SignConvention.Active.export_factor == -1

        assert SignConvention.Passive.is_export(10)
        assert not SignConvention.Active.is_export(10)
        assert not SignConvention.Passive.is_export(-10)
        assert SignConvention.Active.is_export(-10)
        assert not SignConvention.Active.is_export(0)

        assert not SignConvention.Passive.is_import(10)
        assert SignConvention.Active.is_import(10)
        assert SignConvention.Passive.is_import(-10)
        assert not SignConvention.Active.is_import(-10)
        assert not SignConvention.Active.is_import(0)
