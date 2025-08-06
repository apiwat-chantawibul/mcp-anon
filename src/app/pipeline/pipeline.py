from typing import Self
from contextlib import contextmanager
import os
import json

from pydantic import (
    BaseModel,
    SerializeAsAny,
)
import yaml

from .step_union import (
    AnyLoad,
    AnyExport,
)
from .transform_sequence import TransformSequence


@contextmanager
def ensure_file(file_or_path, **kwargs):
    """Opens a file if given a path-like object"""
    is_path = isinstance(file_or_path, (str, bytes, os.PathLike))
    if is_path:
        with open(file_or_path, **kwargs) as f:
            yield f
    else:
        yield file_or_path


class Pipeline(BaseModel):
    """Pipeline for loading, transforming, and exporting dataset"""

    # TODO: Validate dataset type is compatible.
    # This will matter when pipeline could act on pandas.DataFrame or xarray.Dataset.
    load: AnyLoad | None = None
    transform: TransformSequence = TransformSequence()
    export: AnyExport | None = None

    def to_file(self, path_or_file):
        """Save pipeline definition as a file"""
        with ensure_file(path_or_file, mode = 'w') as f:
            # TODO: Make dumped yaml more concise by excluding default values.
            # Simple exclude_defaults option does not work because it also excluded union tags.
            yaml.safe_dump(
                self.model_dump(mode = 'json'),
                f,
            )

    @classmethod
    def from_file(cls, path_or_file) -> Self:
        """Load pipeline definition from file"""
        with ensure_file(path_or_file) as f:
            doc = yaml.safe_load(f) or {}
        return cls.model_validate(doc)

