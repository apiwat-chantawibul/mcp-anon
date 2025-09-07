from typing import Literal

import pandas as pd
from pydantic import (
    Field,
)

from ..step import Transform


class MaskTransform(Transform[pd.DataFrame]):
    """Replaced matched substring with masking characters"""

    type: Literal['mask'] = 'mask'
    field: str = Field(
        description = 'Name of field to transform by masking',
    )
    regex: str = Field(
        description = 'Regular expression matching substring to be masked',
    )
    mask_char: str = Field(
        '*',
        description = 'Character to replace matched substrings',
        min_length = 1,
        max_length = 1,
    )
    n: int = Field(
        -1,
        description = (
            'Number of replacements to make from the start.'
            ' Value of -1 causes all matches to be replaced.'
        ),
        ge = -1,
    )

    def __call__(self, ds: pd.DataFrame) -> pd.DataFrame:
        args = {
            'pat': self.regex,
            'n': self.n,
            'repl': (lambda m: self.mask_char * (m.end() - m.start())),
            'regex': True,
        }
        original = ds[self.field]
        try:
            ds[self.field] = original.str.replace(**args)
        except NotImplementedError as e:
            # FIXME: pyarrow string series currently does not support .str.replace()
            # https://github.com/pandas-dev/pandas/blob/7f670c17cd815a14167734abe5f3ad6e2b15d94d/pandas/core/arrays/_arrow_string_mixins.py#L179
            if 'replace is not supported' in str(e):
                ds[self.field] = original.astype('str').str.replace(**args).astype('string[pyarrow]')
        return ds

