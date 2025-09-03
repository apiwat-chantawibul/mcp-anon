from typing import Literal
from pathlib import Path

from pydantic import (
    BaseModel,
)
import pandas as pd

from ..step import Export


class ExportCsv(Export[pd.DataFrame]):
    type: Literal['csv'] = 'csv'
    path: Path

    def __call__(self, ds: pd.DataFrame) -> None:
        self.path.parent.mkdir(parents = True, exist_ok = True)
        ds.to_csv(self.path, index = False)

