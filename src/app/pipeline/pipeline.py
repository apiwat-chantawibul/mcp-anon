from pydantic import (
    BaseModel,
    SerializeAsAny,
)

from .step import (
    Load,
    Transform,
    TransformSequence,
    Export,
)


class Pipeline[Dataset](BaseModel):
    """Pipeline for loading, transforming, and exporting dataset"""

    load: SerializeAsAny[Load[Dataset]] | None = None
    transform: SerializeAsAny[Transform[Dataset]] = TransformSequence()
    export: SerializeAsAny[Export[Dataset]] | None = None

