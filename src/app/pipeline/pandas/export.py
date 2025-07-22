from typing import Literal

from pydantic import (
    BaseModel,
    FilePath,
)
import pandas as pd

from ..step import Export


class ExportCsv(Export[pd.DataFrame]):
    type: Literal['csv'] = 'csv'
    path: FilePath

    def __call__(self, ds: pd.DataFrame) -> None:
        pd.to_csv(self.path, index = False)

