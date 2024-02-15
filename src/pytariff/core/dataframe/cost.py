import pandas as pd
from pytariff.core.dataframe.profile import MeterProfileSchema

import plotly.express as px  # type: ignore


class TariffCostSchema(MeterProfileSchema):
    """A ``Pandera.DataFrameModel`` class that contains a DateTimeIndex-like index and several ``float``
    columns, being ``total_cost``, ``import_cost``, and ``export_cost``, which are described below.
    Each parameter is a column in the DataFrame schema.

    This Schema is intended to be generated via a call to the :ref:`MeterProfileHandler` ``apply_to`` method.

    Args:
        idx (AwareDateTime): A pandas.DateTimeIndex equivalent from ``Pandera``, that requires
                             that each index key must be unique and timezone-aware (not
                             necessarily possessing the same timezone information in each key).
                             Data is coerced from the provided format into ``AwareDateTime`` type, if possible.
        profile (float): The metering data against which a tariff may be levied. Must be strictly a float.
        total_cost (float): The sum of the ``import_cost`` and ``export_cost`` columns.
        import_cost (float): The amount paid due to import charges.
        export_cost (float): The amount paid due to exprot charges. A negative value is revenue generated.
    """

    total_cost: float
    import_cost: float
    export_cost: float
    # billed_total_cost: float  # the cumulative billed amount, levied at each billing interval
    # TODO billing is complex. leave it for later


class TariffCostHandler:
    """A Handler class which accepts a ``pandas.DataFrame`` and validates it against the ``TariffCostSchema``
    definition.

    Args:
        profile (pd.DataFrame): Must be coercible to the :class:`MeterPofileSchema` format
                                (via ``MeterProfileSchema(profile)``)

    Raises:
        Exception: If the provided ``pandas.DataFrame`` cannot be coerced into the ``MeterProfileSchema`` format.
    """

    def __init__(self, profile: pd.DataFrame) -> None:
        self.profile = profile

    def plot(self, include_additional_cost_components: bool = False) -> None:
        """Plots the information contained in ``self.profile`` using a Plotly express backend.
        Optionally, the user can choose to include all cost components that are not explicitly included
        in the ``TariffCostSchema`` definition.

        Args:
            include_additional_cost_components (bool, default=False): Whether to include intermediate cost
                                                                      components in the plot, which can include costs
                                                                      from each child ``block`` and ``charge``
                                                                      combination.
        """

        profile_copy = self.profile.copy()
        if not include_additional_cost_components:
            profile_copy = profile_copy[["profile", "import_cost", "export_cost", "total_cost"]]
        fig = px.line(profile_copy)
        fig.show()
