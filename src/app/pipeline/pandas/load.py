from typing import Literal

from pydantic import (
    BaseModel,
    FilePath,
)
import pandas as pd

from ..step import Load


class LoadCsv(Load[pd.DataFrame]):
    type: Literal['csv']
    path: FilePath

    def __call__(self) -> pd.DataFrame:
        return pd.read_csv(self.path)

