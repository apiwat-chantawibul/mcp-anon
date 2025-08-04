from typing import Literal

import pandas as pd

from .step import Transform
from .step_union import AnyTransform


class TransformSequence(Transform[pd.DataFrame]):
    """Transformation built from a sequential chain of others"""

    type: Literal['sequence'] = 'sequence'
    sequence: list[AnyTransform] = []

    def __call__(self, ds: pd.DataFrame) -> pd.DataFrame:
        for transform in self.sequence:
            ds = transform(ds)
        return ds

