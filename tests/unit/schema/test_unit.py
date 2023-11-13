from utal.schema import unit


def test_consumption_unit():
    """TODO"""

    # assert that the ConsumptionUnit enum is a subclass of the TariffUnit
    assert issubclass(unit.ConsumptionUnit, unit.TariffUnit)

    # assert the enum has all of the expected members
    members = [m.name for m in unit.ConsumptionUnit]
    assert "kWh" in members


def test_demand_unit():
    """TODO"""

    # assert that the DemandUnit enum is a subclass of the TariffUnit
    assert issubclass(unit.DemandUnit, unit.TariffUnit)

    # assert the enum has all of the expected members
    members = [m.name for m in unit.DemandUnit]
    assert "kW" in members


def test_rate_currency():
    """TODO"""

    # assert the enum has all of the expected members
    members = [m.name for m in unit.RateCurrency]
    assert "AUD" in members
