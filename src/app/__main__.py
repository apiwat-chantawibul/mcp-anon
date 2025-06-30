from pathlib import Path
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field
import pandas as pd


# Server state
state = {
    'datasource': None,
}


mcp = FastMCP(
    name = 'Data Anonymization Toolbox',
    instructions = """
        This server contains tools to examine sensitive dataset
        and build an automated pipeline that export anonymized data from it.

        Tools are named with `OBJECT_` prefix to indicate the object they operate on.
        An additional prefix, such as `OBJECT_ACTION_`, specifies the action performed on that object.
        For example,

        - `dataset_*` tools perform actions on dataset.
        - `dataset_select_*` tools allow client to select datasource that is the target of anonymization pipeline.
          The server must already have access to the datasource selected.
          The client merely "select" which dataset to work on.
        - `dataset_examine_*` tools allow client to see limited views of end user's sensitve dataset.
          Client can obtain dataset schemas, statistics, and synthetic examples but not the underlying sensitive data.
          Client can use "examine" tools to get and understanding of the hidden dataset
          and then use "build" tools to construct procedure that will export anonymized dataset.

        - `pipeline_*` tools perform actions on anonymization pipeline being built such as
          adding, editing, or deleting steps in the pipeline.
        - `pipeline_examine_*` tools allow client to review the current shape of pipeline and the Python code that would be produced.
        - `pipeline_evaluate_*` measures the level of anonymity that current pipeline satisfy.
          For example, it can check that data resulting fromt the pipeline satisfy which level of k-anonymity.

        In current implementation, a selected dataset is essentially represented as a pandas DataFrame object on the server.
        Client can expect operations on dataset to corresponds to some pandas operations on DataFrame in general.
    """,
)


@mcp.tool
async def dataset_select_csv_file(
    path: Annotated[
        str,
        Field(description = (
            'Path inside the server to CSV file.'
            ' This is not path inside MCP client.'
            ' Use path given by user as-is, even if it is relative path.'
        )),
    ],
) -> bool:
    """Select a CSV file as datasource to be anonymized.

    The server will remember the selected source in further interaction.
    """
    path = Path(path)
    # TODO: Handle error
    state['datasource'] = pd.read_csv(path)


@mcp.tool
async def dataset_examine_schema() -> str:
    """Get name and datatype of each field in the selected datasource.

    The returned data will be a CSV where:

    - the first row is header
    - the first column is field names
    - the second column is datatypes
    """
    # TODO: can we return structured data?
    return state['datasource'].dtypes.to_csv(
        index_label = 'field_name',
        header = ['datatype'],
    )


if __name__ == '__main__':
    mcp.run()

