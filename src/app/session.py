import pandas as pd
from pydantic import (
    BaseModel,
    ConfigDict,
)

from app.pipeline import Pipeline


class Session(BaseModel):
    """State of interaction with a particular client"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # TODO: support multi-table like xarray dataset
    dataset: pd.DataFrame | None = None
    pipeline: Pipeline | None = None

