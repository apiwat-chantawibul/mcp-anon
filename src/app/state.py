import pandas as pd
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.pipeline import Pipeline


class State(BaseModel):
    """Application state of mcp-anon server"""

    model_config = ConfigDict(arbitrary_types_allowed = True)

    # TODO: support multi-table like xarray dataset
    dataset: pd.DataFrame | None = Field(
        None,
        description = (
            'Cache pipeline expected result.'
            ' Should not change when pipeline is reran.'
        ),
    )
    pipeline: Pipeline | None = None

