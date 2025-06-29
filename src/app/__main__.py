from pathlib import Path

from fastmcp import FastMCP
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

        There are 4 groups of tools:

        1. "select" dataset
        2. "examine" dataset
        3. "build" pipeline
        4. "evaluate" pipeline

        "select" tools allow client to select datasource that is the target for anonymization.
        The server must already have access to the datasource selected.
        The client merely "select" which dataset to work on.

        "examine" tools allow client to see limited views of end user's sensitve dataset.
        Client can obtain dataset schemas, statistics, and synthetic examples but not the underlying sensitive data.
        Client can use "examine" tools to get and understanding of the hidden dataset
        and then use "build" tools to construct procedure that will export anonymized dataset.

        "build" tools allow client to add, edit, delete steps of data anonymization pipeline.
        "build" tools also provide introspection tools that let client review the shape of current pipeline
        and the Python code that would be produced.

        "evaluate" measures the level of anonymity that current pipeline satisfy.
        For example, it can check that data resulting fromt the pipeline satisfy which level of k-anonymity.
    """,
)


@mcp.tool
async def select_csv_file(path: str) -> bool:
    """Select a CSV file as datasource to be anonymized.

    The server will remember the selected source in further interaction.
    """
    path = Path(path)
    # TODO: Handle error
    state['datasource'] = pd.read_csv(path)


@mcp.tool
async def examine_schema() -> str:
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

