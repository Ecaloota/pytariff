# UTaL

### United Tariff Library for Electrical Tariffs.

Generic intro here


## Installation


## Basic Usage


<!-- ## General Schema

### GenericTariff
A GenericTariff is a closed timezone-aware datetime.datetime interval over [start, end]. One GenericTariff contains up to many children TariffInterval instances, which must share a timezone with their parent.

### TariffInterval
A TariffInterval is a timezone-aware right-open datetime.time interval which is associated with a single TariffCharge and evaluated on DaysApplied.

### TariffCharge
A TariffCharge is a set of TariffBlocks.

### TariffBlock
A TariffBlock is a right-open float interval over [from_quantity, to_quantity] in some 
defined unit of quantity which associates that interval which some TariffRate.

### TariffRate
A TariffRate is a monetary value applied in some registered currency.
 -->


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