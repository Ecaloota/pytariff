from utal.schema.generic_tariff import GenericTariff


class FlatConsumptionTariff(GenericTariff):
    """A FlatTariff is a subclass of a GenericTariff, which is distinguished by
    containing a single Rate in a single Block"""

    # TODO A FlatConsumptionTariff is distinguished from a GenericTariff by having greater
    # restrictions on its children; specifically, a FlatConsumptionTariff should have only a single
    # TariffInterval, which itself should have a ConsumptionCharge (only) containing (only) one
    # ConsumptionBlock; the ConsumptionBlock should have a from_quantity = 0 and to_quantity = float("inf")

    pass
