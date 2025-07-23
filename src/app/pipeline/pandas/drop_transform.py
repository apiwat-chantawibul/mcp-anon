from typing import Literal

import pandas as pd
from pydantic import (
    Field,
    conlist,
)

from ..step import Transform


class DropTransform(Transform[pd.DataFrame]):
    """Remove fields from dataset"""

    type: Literal['drop'] = 'drop'
    fields: str | list[str] = Field(
        description = 'List of fields to be dropped',
        min_length = 1,
    )

    def __call__(self, ds: pd.DataFrame) -> pd.DataFrame:
        return ds.drop(columns = self.fields)

