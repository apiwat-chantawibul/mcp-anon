from pathlib import Path
from typing import Annotated, Union
from contextlib import asynccontextmanager

from fastmcp import (
    FastMCP,
    Context,
)
from pydantic import (
    Field,
)
import pandas as pd

from app.state import State
from app.pipeline.pandas.load import LoadCsv
from app.dataset.view.schema import get_dataset_schema, DatasetSchema
from app.dataset.view.stats import get_dataset_stats, DatasetStats


LoadConfig = Annotated[
    Union[LoadCsv],
    Field(
        discriminator = 'type',
    ),
]


@asynccontextmanager
async def lifespan(app: FastMCP):
    app.state = State()
    yield


app = FastMCP(
    name = 'Data Anonymization Toolbox',
    instructions = """
        This MCP server helps you examine sensitive datasets and build
        automated pipelines to export anonymized data.
        
        A pipeline consist of three sequential phases --- load, tranform, and export.

        - `loader` gets data from source into working memory.
        - `transformer` modifies data in memory.
        - `exporter` outputs data after loading and transforming.

        Tools are named with an OBJECT_ACTION_ prefix.
        Available objects are:

        - `loader`, `transformer`, `exporter` are as mentioned above.
        - `pipeline` refers all phases of pipeline together.
        - `original` refers to dataset just after being loaded, but not yet transformed.
        - `result` refers to dataset after all transformations.

        For example,

        - `original_view_*` and `result_view_*` view limited, non-sensitive
          aspects of the dataset (schemas, statistics, synthetic examples) to
          understand its structure and content without exposing raw data. This
          helps you plan your anonymization pipeline.
        - `transformer_append_binning` add a new step at the end of transformer
          sequence which generalizes a column by binning its value.
        - `result_evaluate_k_anonymity` Assess the k-anonymity level of resulting dataset.

        # Development status

        Some tools might not have been implemented yet.

        Currently, selected datasets are treated as pandas DataFrames on the
        server, so you can generally expect dataset operations to align with
        pandas functionalities.
    """,
    lifespan = lifespan,
)


@app.tool
async def loader_set(
    load: LoadConfig,
    ctx: Context,
):
    """Specify source of data to be anonymized.

    - The server will remember the selected source for further operations.
    - Since the goal is to build pipeline,
      you can use representative example of the dataset instead of raw dataset.
    - The source need not be the actual or whole data.
      It just need to be representative so pipeline can be designed based on its structure.
    - Paths and URIs are resolved from server perspective, not the client's.
    """
    pipeline = ctx.fastmcp.state.pipeline
    if pipeline.load is not None:
        # TODO: return previous load config when replacing.
        raise NotImplementedError('Can not replace loader once set')
    pipeline.load = load
    # TODO: return source general shape
    # TODO: return how the source is being read


@app.tool
async def loader_describe(
    ctx: Context,
) ->  LoadConfig | None:
    """Describe current configuration of loader."""
    return ctx.fastmcp.state.pipeline.load


@app.tool
async def original_view_schema(
    ctx: Context,
) -> DatasetSchema:
    """Get name and datatype of each field in original dataset."""
    return get_dataset_schema(ctx.fastmcp.state.original_dataset)


@app.tool
async def result_view_schema(
    ctx: Context,
) -> DatasetSchema:
    """Get name and datatype of each field in result dataset."""
    return get_dataset_schema(ctx.fastmcp.state.result_dataset)


@app.tool
async def original_view_stats(
    ctx: Context,
) -> DatasetStats:
    """Get summary statistics on original dataset.

    This corresponds to `pandas.DataFrame.describe()`.
    """
    # TODO: worry about leaking sensitive data through statistics
    return get_dataset_stats(ctx.fastmcp.state.original_dataset)

