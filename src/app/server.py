from pathlib import Path
from typing import Annotated, Union
from contextlib import asynccontextmanager
from inspect import cleandoc

from fastmcp import (
    FastMCP,
    Context,
)
from pydantic import (
    BaseModel,
    Field,
    model_validator,
)
import pandas as pd

from app.state import State, PipelineView
from app.pipeline import CustomTransform
from app.pipeline.pandas import LoadCsv, LoadSql, BinTransform, DropTransform
from app.dataset.view.schema import get_dataset_schema, DatasetSchema
from app.dataset.view.stats import get_dataset_stats, DatasetStats


@asynccontextmanager
async def lifespan(app: FastMCP):
    app.state = State()
    yield


app = FastMCP(
    name = 'Data Anonymization Toolbox',
    instructions = """
        This MCP server helps you examine sensitive datasets and build
        automated pipeline to export anonymized data.
        
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


LoaderConfig = Annotated[
    Union[LoadCsv, LoadSql],
    Field(
        discriminator = 'type',
        description = 'Configuration for dataset loader',
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


@app.tool
async def loader_set(
    loader_config: LoaderConfig,
    ctx: Context,
) -> DatasetSchema:
    """Specify source of data to be anonymized.

    - The server will remember the selected source for further operations.
    - Since the goal is to build pipeline,
      you can use representative example of the dataset instead of raw dataset.
    - The source need not be the actual or whole data.
      It just need to be representative so pipeline can be designed based on its structure.
    - Paths and URIs are resolved from server perspective, not the client's.

    On success, immediately return result from original_dataset_schema tool.
    """
    pipeline = ctx.fastmcp.state.pipeline
    if pipeline.load is not None:
        # TODO: return previous load config when replacing.
        raise NotImplementedError('Can not replace loader once set')
    pipeline.load = loader_config
    return await original_view_schema.fn(ctx)


@app.tool
async def loader_describe(
    ctx: Context,
) ->  LoaderConfig | None:
    """Describe current configuration of loader."""
    load = ctx.fastmcp.state.pipeline.load
    if load is None:
        return None
    return load


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
    """Get summary statistics on original dataset."""
    # TODO: worry about leaking sensitive data through statistics
    return get_dataset_stats(ctx.fastmcp.state.original_dataset)


@app.tool
async def result_view_stats(
    ctx: Context,
) -> DatasetStats:
    """Get summary statistics on result dataset."""
    return get_dataset_stats(ctx.fastmcp.state.result_dataset)


TransformerConfig = Annotated[
    Union[
        BinTransform,
        DropTransform,
        CustomTransform[pd.DataFrame],
    ],
    Field(
        discriminator = 'type',
        description = 'Configuration for a transformation step',
    ),
]


# TODO: return tranformation ID
# - so it can be referenced when deleting
# - ID format should be semantic.
# TODO: maybe allow adding tranform at different places in transformer
# but defaulting to at the end?
@app.tool
async def transformer_append(
    transform: TransformerConfig,
    ctx: Context,
) -> PipelineView:
    """Append a new step at the end of transformer sequence.

    - The transform will be immediately tested against dataset.
    - If the transform causes error, it will not be appended to sequence.

    Returns definition of current pipeline on success.
    """
    ctx.fastmcp.state.append_transform(transform)
    return ctx.fastmcp.state.view_pipeline()


# TODO: Optionally let client focus on specific part.
# Maybe by specifying ID of component.
# TODO: Optionally show source code implementation
@app.tool
async def pipeline_view(
    ctx: Context,
) -> PipelineView:
    """Get status of current pipeline"""
    return ctx.fastmcp.state.view_pipeline()


# NOTE: Can not use
#
#     arg: str = Field(default = ..., description = ...)
#
# pattern because there seems to be a bug in mcp library that does not extract
# default value from Field properly. Instead, we need to use
#
#     arg: Annotated[str, Field(description = ...)] = ...
@app.prompt
def generate_request_to_construct_anonymization_pipeline(
    datasource: Annotated[
        str,
        Field(
            description = cleandoc("""
                Describe where the dataset is.
                Could be a path to CSV file on mcp-anon server.
                Or it could be a connection URL to database.
            """),
            examples = [
                'target/examples.csv file on the server',
                'postgresql://localhost:5432/database',
            ],
        ),
    ],
    data_description: Annotated[
        str,
        Field(
            description = 'What kind of dataset it is. What personal information does it contain.',
            examples = [
                'The dataset contains employee salary',
                'The dataset is from a customer survey',
            ],
        ),
    ] = '',
    purpose: Annotated[
        str,
        Field(
            description = 'How will the anonymized data be used. Who is the audience.',
            examples = [
                'archive for long-term storage',
                'make available publicly',
            ],
        ),
    ] = '',
    threat_actor: Annotated[
        str,
        Field(
            description = cleandoc("""
                Who are you protecting the sensitive data from?
                What are their objectives?
                What resources do they have?
                What external data they might have access to that help with re-identification?
            """),
            examples = [
                'financially motivated actors',
                'nation-state actors'
                'ideologues (hacktivists and terrorists)',
                'thrill seekers and trolls',
                'insiders',
                'competitors',
            ],
        ),
    ] = '',
    legal_framework: Annotated[
        str,
        Field(
            description = cleandoc("""
                What legal framework should we be concerned about.
                For example, specific law of specific country.
            """),
        ),
    ] = 'GDPR',
) -> str:
    """Generate user request to construct anonymization pipeline"""
    sections = [
        f"""
            Help me create a Python pipeline to anonymize a dataset using "Data
            Anonymization Toolbox" MCP server. The dataset is from:

            {datasource}
        """,
        data_description,
        purpose and f"""
            The anonymized dataset should be fit to {purpose}
        """,
        threat_actor and f"""
            The likely threat actors we wish to protect the sensitive data from are:

            {threat_actor}
        """,
        legal_framework and f"""
            Consider the legal framework of {legal_framework}
            when evaluating if resulting dataset is fit for purpose.
        """,
        """
            Guide me through the following steps:

            - First, examine the dataset schema.
            - Classify fields into one of the following classes:
              - "Direct identifier": Data unique to individual which an attacker can
                directly use to identify data subject.
              - "Indirect identifier": Data not unique to individual but attacker may
                use in combination with other fields or external data to re-identify data subject.
              - "Sensitive attribute"
              - "Ambiguous": Can not classify yet.
                For exmaple, field name might be unclear.
                Or field contain free-form text.
            - Get my feedback on the field classification.
              Ask for missing information needed to classify currently ambiguous fields.
            - Once there are no more ambiguous fields,
              apply anonymization technique step-by-step.
              Confirming how the dataset changed at each step and explain the step to me.
            - Evaluate the anonymity of resulting dataset.
            - Export the pipeline program and give it to me.
        """,
    ]
    prompt = '\n\n'.join(map(cleandoc, filter(None, sections)))
    return prompt

