# UTaL

### United Tariff Library for Electrical Tariffs.

Generic intro here


## Installation

<!-- TODO. Some sort of pip install -->

## Basic Usage

<!-- TODO. Code snippets demonstrating viewing of simple TOU tariff against usage -->

## Schema

This library defines five classes of electrical tariff:
1. GenericTariff
2. SingleRateTariff
3. TimeOfUseTariff
4. DemandTariff
5. ConsumptionTariff
6. BlockTariff

### GenericTariff
A GenericTariff is a generalised model of an electrical tariff defined as a closed timezone-aware datetime interval. It contains child TariffIntervals, which are right-open timezone-aware time intervals which are levied on their DaysApplied and associated with a single TariffCharge. A TariffCharge contains a tuple of TariffBlocks, each of which define the right-open interval of some unit over which a given TariffRate is to be applied.

```python3
GenericTariff(
    TariffInterval(
        TariffCharge(
            TariffBlock,
            [...]
        ),
        [...]
    ),
    [...]
)
```

Using this model, it is possible to define many different subclasses of tariff. The most common subclasses are implemented already and provided below, with their implied restrictions applied in these child classes.

---
### SingleRateTariff
A SingleRateTariff is a subclass of a GenericTariff that enforces that, among other things:
1. The tariff must define only a single child TariffInterval (meaning it can only contain one TariffCharge)
2. That single TariffCharge must contain at least one block, from zero to infinite usage of its TariffUnit. It may also contains at most a single block from zero to infinite usage of its TariffUnit in each of the two TradeDirections (Import and Export).

---
### TimeOfUseTariff
A TimeOfUseTariff is a subclass of a GenericTariff that enforces that, among other things:
1. More than one unique child TariffInterval must be defined
2. These TariffIntervals must share their DaysApplied and timezone attributes, and contain unique, non-overlapping [start, end) intervals

There are no restrictions preventing each child TariffInterval in the TimeOfUseTariff from containing multiple non-overlapping 
blocks, and no restriction on the existence of reset periods on each TariffInterval. A TimeOfUseTariff can be defined in terms of 
either Demand or Consumption units (but not both).

---
### DemandTariff
A DemandTariff is a subclass of a GenericTariff that enforces that, among other things:
1. At least one child TariffInterval must be defined
2. The child TariffInterval(s) must use Demand units (e.g. kW)

There are no restrictions preventing each child TariffInterval in the DemandTariff from containing multiple non-overlapping
blocks, and no restriction on the existence of reset periods on each TariffInterval. In practice, it is expected that a 
DemandTariff will contain multiple blocks and a non-None reset period.

---
### ConsumptionTariff
A ConsumptionTariff is a subclass of a GenericTariff that enforces that, among other things:
1. At least one child TariffInterval must be defined
2. The child TariffInterval(s) must use Consumption units (e.g. kWh)

There are no restrictions preventing each child TariffInterval in the ConsumptionTariff from containing multiple blocks,
and no restriction on the existence of reset periods on each TariffInterval.

---
### BlockTariff
A BlockTariff is a subclass of a GenericTariff that enforces that, among other things:
1. At least one child TariffInterval must be defined
2. The child TariffInterval(s) must each contain more than a single non-overlapping block

There are no restrictions on the units of the child TariffIntervals or the existence of reset periods.




<!-- 
Wishlist:

1. Write Pandera schema to define validated pandas series which can serve as 
    input to tariffs.
    Example usage for some tariff t: result_schema_inst = t.apply(profile_instance),
    where the result schema defines charges over time and information about calculation input types
    and billing periods, etc
2. Plotting methods for result schema and profile schema, for visual inspection + debug
2. Write a FastAPI or similar to serve results via basic endpoints which perform above
3. Write a set of db table schema for a simple sqlite db which we can add tariffs to (portable)
4. Simple html interface which allows selection from pre-defined tariffs in db and provision of 
    json profile inputs

 -->