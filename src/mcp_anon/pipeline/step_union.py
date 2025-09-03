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
    ExportCsv,
)
from .custom_transform import CustomTransform


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
        # TODO: Include TransformSequence as part of AnyTransform.
        #
        # While I could use "forward reference" feature of pydantic to resolve
        # mutual dependency between TransformSequence and AnyTransform, but
        # it seems like this confuses FastMCP making it fail integration tests.
    ],
    Field(
        discriminator = 'type',
        description = 'Configuration for a transformation step',
    ),
]


AnyExport = Annotated[
    Union[ExportCsv],
    Field(
        discriminator = 'type',
        description = 'Configuration for a dataset exporter',
    ),
]

