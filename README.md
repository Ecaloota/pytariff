# PyTariff

<!-- Badges go here TODO -->

PyTariff is a library for the generic representation of electrical tariffs in domain models.

## Installation

```bash
pip install pytariff
```

## Basic Usage: Defining a Tariff

In the below example, we create a simple time-of-use tariff consisting of a single import charge and a single export charge. The tariff is defined over the time period from the first of January 2023 until the first of January 2024 in UTC.

The import charge is applied at all times of day (because ```start_time=time(0)``` and ```end_time=time(0))```), on all days within the tariff definition period without exceptions for holidays. It defines a single charge on the ```Consumption``` of energy in kWh in the ```Import``` ```TradeDirection``` with a value of 20.0 units in Australian dollars over the consumption range from 0 kWh to infinite kWh imported. 

The charge is reset every three months (quarterly), starting from the anchor datetime, which is not useful in this example but becomes relevant if the ```UsageChargeMethod``` is not ```identity```. Other ```UsageChargeMethod```s allow the user to define a tariff which charges on maximum demand in a quarter, for example, reset each quarter. The export charge is similar, but defined in the oposite ```TradeDirection```.

Naturally, many other combinations are possible. Obvious restrictions on tariff construction is achieved by using specific subclasses of the base PyTariff ```GenericTariff``` object, such as the ```TimeofUseTariff``` shown below, or other classes such as the ```BlockTariff``` or ```MarketTariff```, to name a few.

```python3
import pytariff as pt
from zoneinfo import ZoneInfo
from datetime import datetime, time


# Define a Time-Of-Use Tariff with import and export charges
import_charge = pt.TariffInterval(
    start_time=time(0),
    end_time=time(0),
    days_applied=pt.DaysApplied(day_types=pt.DayType.ALL_DAYS),
    tzinfo=ZoneInfo("UTC"),
    charge=pt.TariffCharge(
        blocks=(
            pt.TariffBlock(
                rate=pt.TariffRate(currency="AUD", value=20.0),
                from_quantity=0.0,
                to_quantity=float("inf")
            ),
        ),
        unit=pt.TariffUnit(
            metric=pt.Consumption.kWh,
            direction=pt.TradeDirection.Import,
            convention=pt.SignConvention.Passive
        ),
        reset_data=pt.ResetData(
            anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")),
            period=pt.ResetPeriod.FIRST_OF_QUARTER
        ),
        method=pt.UsageChargeMethod.identity,
    ),
)

# define the export charge
export_charge = pt.TariffInterval(
    start_time=time(0),
    end_time=time(0),
    days_applied=pt.DaysApplied(day_types=pt.DayType.ALL_DAYS),
    tzinfo=ZoneInfo("UTC"),
    charge=pt.TariffCharge(
        blocks=(
            pt.TariffBlock(
                rate=pt.TariffRate(currency="AUD", value=-1.0),
                from_quantity=0.0,
                to_quantity=float("inf")
            ),
        ),
        unit=pt.TariffUnit(
            metric=pt.Consumption.kWh,
            direction=pt.TradeDirection.Import,
            convention=pt.SignConvention.Passive
        ),
        reset_data=pt.ResetData(
            anchor=datetime(2023, 1, 1, tzinfo=ZoneInfo("UTC")),
            period=pt.ResetPeriod.FIRST_OF_QUARTER
        ),
        method=pt.UsageChargeMethod.identity,
    ),
)

# define the parent time-of-use tariff
tou_tariff = TimeOfUseTariff(
    start=datetime(2023, 1, 1),
    end=datetime(2024, 1, 1),
    tzinfo=ZoneInfo("UTC"),
    children=(import_charge, export_charge),
)
```

## Basic Usage: Applying a Tariff to Metering Data

Now that we have defined a tariff, we are able to investigate how costs are levied against energy usage. Before we begin, we must define metering data for the tariff to be applied towards, and provide a ```MeterProfileHandler``` which can be used by PyTariff:

```python3
import pandas as pd
import numpy as np
from zoneinfo import ZoneInfo

meter_profile = pd.DataFrame(
    index=pd.date_range(
        start="2022-12-31T00:00:00",
        end="2023-01-04T00:00:00",
        tz=ZoneInfo("UTC"),
        freq="1h",
        inclusive="left",
    ),
    data={"profile": np.tile(np.array([0.0] * 8 + [5.0] * 8 + [-1.0] * 8), 3)},
)

handler = MeterProfileHandler(meter_profile)
cost_df = tou_tariff.apply_to(
    handler,
    tariff_unit=TariffUnit(
        metric=Consumption.kWh,
        convention=SignConvention.Passive
    ),
)

```


We can call ```.apply_to``` with our ```MeterProfileHandler``` and a ```TariffUnit``` which specifies that the metering data provided has the same units are the TariffCharges to which is it applied, and ensures the ```SignConvention``` of the metering data is respected (as either Active or Passive).


The output ```cost_df``` contains a breakdown of the costs by ```TariffCharge``` and ```TariffBlock``` combinations in each of the ```TradeDirection```s. It also contains columns which tally the total ```import_cost```, ```export_cost```, and ```total_cost```. This dataframe, and all the cost components, can be easily visualised by passing the results to a ```TariffCostHandler```:

```python3
cost_handler = TariffCostHandler(cost_df)
cost_handler.plot(include_additional_cost_components=True)
```

![Example TOU Tariff](src/pytariff/docs/img/tou_example.png)


<!-- ## Schema

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

---
### MarketTariff
A MarketTariff is a subclass of a GenericTariff that enforces that, among other things:
1. At least one child TariffInterval must be defined
2. The child TariffInterval(s) must each contain only a single block in their TariffCharge
3. Each TariffCharge rate must be defined as a MarketRate

There are no restrictions on the units of the child TariffIntervals or the existence of reset periods. A MarketTariff cannot use TariffRate(s). Tariff values for MarketRates are
determined on-the-fly from input data when applied to metering data. -->
