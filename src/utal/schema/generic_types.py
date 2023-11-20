from typing import Generic, TypeVar

T = TypeVar("T", bound=object)


class Consumption(Generic[T]):
    pass


class Demand(Generic[T]):
    pass


GenericType = TypeVar("GenericType", Demand, Consumption)
