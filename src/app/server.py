from pathlib import Path
from typing import Annotated
from contextlib import asynccontextmanager

from fastmcp import (
    FastMCP,
    Context,
)
from pydantic import Field
import pandas as pd

from app.state import State


@asynccontextmanager
async def lifespan(app: FastMCP):
    app.state = State()
    yield


app = FastMCP(
    name = 'Data Anonymization Toolbox',
    instructions = """
        This MCP server helps you examine sensitive datasets and build
        automated pipelines to export anonymized data.

        Tools are named with an OBJECT_ACTION_ prefix. For example:

        - `dataset_*` tools interact dataset.
          - `dataset_select_*` choose an existing dataset on the server to work with.
          - `dataset_examine_*` view limited, non-sensitive aspects of the
            dataset (schemas, statistics, synthetic examples) to understand its
            structure and content without exposing raw data. This helps you
            plan your anonymization pipeline.
        - `pipeline_*` tools act on anonymization pipeline being built
          (e.g., add, edit, or delete pipeline steps).
          - `pipeline_examine_*` review the pipeline's current configuration and generated Python code.
          - `pipeline_evaluate_*` Assess the anonymity level
            (e.g., k-anonymity) of the data produced by the pipeline.

        Currently, selected datasets are treated as pandas DataFrames on the
        server, so you can generally expect dataset operations to align with
        pandas functionalities.
    """,
    lifespan = lifespan,
)


@app.tool
async def dataset_select_csv_file(
    path: Annotated[
        str,
        Field(description = (
            'Path inside the server to CSV file.'
            ' This is not path inside MCP client.'
            ' Use path given by user as-is, even if it is relative path.'
        )),
    ],
    ctx: Context,
) -> bool:
    """Select a CSV file as datasource to be anonymized.

    The server will remember the selected source in further interaction.
    """
    path = Path(path)
    ctx.fastmcp.state.session.dataset = pd.read_csv(path)
    return True


@app.tool
async def dataset_examine_schema(
    ctx: Context,
) -> str:
    """Get name and datatype of each field in the selected datasource.

    The returned data will be a CSV where:

    - first row is header
    - first column is field names
    - second column is datatypes
    """
    return ctx.fastmcp.state.session.dataset.dtypes.to_csv(
        index_label = 'field_name',
        header = ['datatype'],
    )


@app.tool
async def dataset_examine_stats(
    ctx: Context,
) -> str:
    """Get summary statistics on the selected datasource.

    This corresponds to `pandas.DataFrame.describe()`.
    """
    # TODO: worry about leaking sensitive data through statistics
    return ctx.fastmcp.state.session.dataset.describe().to_csv()

