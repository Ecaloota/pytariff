import pandas as pd
from pytariff.core.dataframe.profile import MeterProfileSchema

import plotly.express as px  # type: ignore


class TariffCostSchema(MeterProfileSchema):
    total_cost: float  # the sum of import cost + export cost
    import_cost: float  # the amount paid due to import
    export_cost: float  # the amount paid due to export (negative value is revenue generated)
    # billed_total_cost: float  # the cumulative billed amount, levied at each billing interval
    # TODO billing is complex. leave it for later


class TariffCostHandler:
    def __init__(self, profile: pd.DataFrame) -> None:
        self.profile = profile

    def plot(self, include_additional_cost_components: bool = False) -> None:
        """"""

        profile_copy = self.profile.copy()
        if not include_additional_cost_components:
            profile_copy = profile_copy[["profile", "import_cost", "export_cost", "total_cost"]]
        fig = px.line(profile_copy)
        fig.show()
