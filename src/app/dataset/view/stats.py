from pydantic import RootModel
import pandas as pd


class FieldStats(RootModel[dict[str, float]]):
    """List statistics for a particular field.

    Maps from statistics name to its value.
    """
    pass


class DatasetStats(RootModel[dict[str, FieldStats]]):
    """Maps from field name its statistics."""
    pass


def get_dataset_stats(df: pd.DataFrame) -> DatasetStats:
    return DatasetStats(
        df.describe().to_dict()
    )

