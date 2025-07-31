from pydantic import (
    BaseModel,
    SerializeAsAny,
)

from .step_union import (
    AnyLoad,
    AnyExport,
)
from .transform_sequence import TransformSequence


class Pipeline(BaseModel):
    """Pipeline for loading, transforming, and exporting dataset"""

    # TODO: Validate dataset type is compatible.
    # This will matter when pipeline could act on pandas.DataFrame or xarray.Dataset.
    load: AnyLoad | None = None
    transform: TransformSequence = TransformSequence()
    # TODO: replace with
    #     export: AnyExport | None = None
    export: None = None

