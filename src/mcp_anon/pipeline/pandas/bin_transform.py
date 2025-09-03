from typing import Any, Literal
import inspect

import pandas as pd
from pydantic import (
    Field,
)

from ..step import Transform


class BinTransform(Transform[pd.DataFrame]):
    """Binning of numeric field"""

    type: Literal['bin'] = 'bin'
    input_field: str = Field(
        description = 'Name of field to transform by binning',
    )
    output_field: str | None = Field(
        None,
        description = inspect.cleandoc("""
            Name of output field.

            If empty, output will replace input field.
        """),
    )
    bins: int | list[Any] = Field(
        description = inspect.cleandoc("""
            If integer, define the number of equal-width bins to be automatically created.
            If list, define bin edges.
        """),
        examples = [
            10,
            [0, 5, 10, 15],
        ],
    )
    include_lowest: bool = Field(
        False,
        description = 'Is the highest bin edge inclusive',
    )
    include_highest: bool = Field(
        True,
        description = 'Is the lowest bin edge inclusive',
    )

    def __call__(self, ds: pd.DataFrame) -> pd.DataFrame:
        ds[self.output_field or self.input_field] = pd.cut(
            ds[self.input_field],
            bins = self.bins,
            right = self.include_highest,
            include_lowest = self.include_lowest,
        )
        return ds

