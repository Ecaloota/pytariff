import pandas as pd
import pandera as pa
from pandera.dtypes import Timestamp
from pandera.typing import DataFrame


class MeterProfileSchema(pa.DataFrameModel):
    column1: Timestamp
    column2: float


class OutputSchema(MeterProfileSchema):
    cost: float


@pa.check_types
def transform(df: DataFrame[MeterProfileSchema]) -> DataFrame[OutputSchema]:
    return df.assign(cost=100.0)  # type: ignore # ??


df = pd.DataFrame(index=[1], data={"column1": pd.Timestamp(2023, 1, 1, unit="ns"), "column2": float(5)})

out = transform(df)  # type: ignore # ??

print(df)
print(out)
