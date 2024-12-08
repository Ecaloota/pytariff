from pytest import Metafunc

from tests.generators import Generators, ParametrizedArgs

GeneratorRegister: dict[str, ParametrizedArgs] = {
    # test_day.py
    "TestDayType.test_day_type_intersection": Generators.day_type_intersection_cases(),
    # test_block.py
    "TestTariffBlock.test_tariff_block_construction": Generators.tariff_block_cases(),
    "TestTariffBlock.test_tariff_block_intersection": Generators.tariff_block_intersections(),
}


def pytest_generate_tests(metafunc: Metafunc):
    if metafunc.function.__qualname__ in GeneratorRegister:
        pargs = GeneratorRegister[metafunc.function.__qualname__]
        metafunc.parametrize(pargs.argnames, pargs.funcargs)
