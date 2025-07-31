from typing import Annotated, Union

from pydantic import (
    BaseModel,
    Field,
)
import pandas as pd

from .pandas import (
    LoadCsv,
    LoadSql,
    BinTransform,
    DropTransform,
)
from .custom_transform import CustomTransform
from .transform_sequence import TransformSequence


AnyLoad = Annotated[
    Union[
        LoadCsv,
        LoadSql,
    ],
    Field(
        discriminator = 'type',
        description = 'Configuration for a dataset loader',
        examples = [
            {'type': 'csv',
             'path': 'input.csv'},
            {'type': 'sql',
             'sql': 'SELECT * FROM table',
             'drivername': 'mysql',
             'host': 'localhost'},
        ],
    ),
]


AnyTransform = Annotated[
    Union[
        BinTransform,
        DropTransform,
        CustomTransform[pd.DataFrame],
        TransformSequence,
    ],
    Field(
        discriminator = 'type',
        description = 'Configuration for a transformation step',
    ),
]
TransformSequence.model_rebuild()


AnyExport = Annotated[
    # TODO: Replace with Union[...],
    None,
    Field(
        discriminator = 'type',
        description = 'Configuration for a dataset exporter',
    ),
]

