import pandera as pa
from pandera.typing import DataFrame
from pydantic import model_validator

from utal.schema.block import ConsumptionBlock
from utal.schema.charge import ConsumptionCharge
from utal.schema.generic_tariff import ConsumptionTariff
from utal.schema.meter_profile import MeterProfileSchema, TariffCostSchema
from utal.schema.tariff_interval import ConsumptionInterval


class FlatConsumptionTariff(ConsumptionTariff):
    """A FlatTariff is a subclass of a GenericTariff, which is distinguished by
    containing a single Rate in a single Block"""

    @model_validator(mode="after")
    def validate_flat_consumption_tariff(self) -> "FlatConsumptionTariff":
        """
        A FlatConsumptionTariff is distinguished from a GenericTariff by having greater
        restrictions on its children; specifically, a FlatConsumptionTariff should have only a single
        TariffInterval, which itself should have a ConsumptionCharge (only) containing (only) one
        ImportConsumptionBlock and/or ExportConsumptionBlock (each);
        The ConsumptionBlock should have a from_quantity = 0 and to_quantity = float("inf")
        """

        if self.children is None:
            raise ValueError

        if len(self.children) != 1:
            raise ValueError

        if not isinstance(self.children[0], ConsumptionInterval):
            raise ValueError

        if not isinstance(self.children[0].charge, ConsumptionCharge):
            raise ValueError

        if not all(isinstance(x, ConsumptionBlock) for x in self.children[0].charge.blocks):
            raise ValueError

        if not self.children[0].charge.blocks[0].from_quantity == 0:
            raise ValueError

        if not self.children[0].charge.blocks[0].to_quantity == float("inf"):
            raise ValueError

        return self

    @pa.check_types
    def apply(self, meter_profile: DataFrame[MeterProfileSchema]) -> DataFrame[TariffCostSchema]:
        return super().apply(meter_profile)
