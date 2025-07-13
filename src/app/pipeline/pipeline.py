from pydantic import (
    BaseModel,
)

from .step import (
    Load,
    Transform,
    TransformSequence,
    Export,
)


class Pipeline[Dataset](BaseModel):
    """Pipeline for loading, transforming, and exporting dataset"""

    load: Load[Dataset] | None = None
    transform: Transform[Dataset] = TransformSequence()
    export: Export[Dataset] | None = None

