from pytest import Metafunc

from tests.generators import (
    DayTypeGenerators,
    DefinedIntervalGenerators,
    ParametrizedArgs,
    TariffBlockGenerators,
    TariffRateGenerators,
)

GeneratorRegister: dict[str, ParametrizedArgs] = {
    # test_day.py
    "TestDayType.test_day_type_intersection": DayTypeGenerators.day_type_intersection_cases(),
    # test_block.py
    "TestTariffBlock.test_tariff_block_construction": TariffBlockGenerators.tariff_block_cases(),
    "TestTariffBlock.test_tariff_block_intersection": TariffBlockGenerators.tariff_block_intersections(),
    "TestTariffBlock.test_tariff_block_ordering": TariffBlockGenerators.tariff_block_ordering_cases(),
    # test_defined_interval.py
    "TestDefinedInterval.test_defined_interval_construction": DefinedIntervalGenerators.defined_interval_construction_cases(),
    # test_rate.py
    "TestTariffRate.test_tariff_rate_get_value_cases": TariffRateGenerators.tariff_rate_get_value_cases(),
}


def pytest_generate_tests(metafunc: Metafunc) -> None:
    if metafunc.function.__qualname__ in GeneratorRegister:
        pargs = GeneratorRegister[metafunc.function.__qualname__]
        metafunc.parametrize(pargs.argnames, pargs.funcargs)
