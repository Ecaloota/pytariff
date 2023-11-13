from utal.schema.generic_tariff import GenericTariff


class BlockConsumptionTariff(GenericTariff):
    """A BlockConsumptionTariff is a subclass of a GenericTariff, which is distinguished by
    containing more than a single Block"""

    # TODO A BlockConsumptionTariff is distinguished from a GenericTariff by having greater
    # restrictions on its children; specifically, a BlockConsumptionTariff should have any number of
    # TariffIntervals, each of which should have a ConsumptionCharge (only) containing (only) > 1
    # ConsumptionBlocks; each ConsumptionBlock has no restriction on the from_quantity and
    # to_quantity values, other than the requirement that they do not overlap.

    pass
