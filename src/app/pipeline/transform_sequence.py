from typing import Literal

import pandas as pd

from .step import Transform


class TransformSequence(Transform[pd.DataFrame]):
    """Transformation built from a sequential chain of others"""

    type: Literal['sequence'] = 'sequence'
    # NOTE: AnyTransform is defined later in .step_union module
    # to avoid circular import
    sequence: list['AnyTransform'] = []

    def __call__(self, ds: pd.DataFrame) -> pd.DataFrame:
        for transform in self.sequence:
            ds = transform(ds)
        return ds

