import logging
_logger = logging.getLogger(__name__)
import pprint

import click
import devtools

from mcp_anon.dataset.view.schema import get_dataset_schema
from .pipeline import Pipeline


pipeline_file_argument = click.argument(
    'pipeline',
    metavar = 'PIPELINE_FILE',
    type = click.File(),
    callback = lambda ctx, param, value: Pipeline.from_file(value),
)


@click.group()
def cli():
    """Use anonymization pipeline files craeted by mcp-anon."""
    pass


@cli.command()
@pipeline_file_argument
def run(pipeline):
    """Run anonymization pipeline."""
    if pipeline.load is None:
        _logger.error('Pipeline has no loader.')
        return

    if pipeline.export is None:
        _logger.error('Pipeline has no exporter.')
        return

    _logger.info(f'Loading dataset from: {pipeline.load.model_dump_json()}')
    ds = pipeline.load()
    print('Loaded dataset schema:')
    devtools.pprint(get_dataset_schema(ds).model_dump(mode = 'json'))
    print('Loaded dataset:')
    print(ds)

    _logger.info('Transforming dataset')
    ds = pipeline.transform(ds)
    print('Transformed dataset schema:')
    devtools.pprint(get_dataset_schema(ds).model_dump(mode = 'json'))
    print('Transformed dataset:')
    print(ds)

    _logger.info(f'Exporting dataset to: {pipeline.load.model_dump_json()}')
    pipeline.export(ds)
    _logger.info('Pipeline ran successfully')


@cli.command()
@click.option(
    '--format', '-f', '_format',
    type = click.Choice([
        'json',
        'python-dict', 'pydict',
        'python-object', 'pyobj',
    ]),
    default = 'pydict',
    show_default = True,
    help = 'Select output format. `py*` format are pretty-printed.',
)
@pipeline_file_argument
def inspect(pipeline, _format):
    """Inspect anonymization pipeline."""
    match _format:
        case 'json':
            print(pipeline.model_dump_json())
        case 'python-dict' | 'pydict':
            devtools.pprint(pipeline.model_dump(mode = 'json'))
        case 'python-object' | 'pyobj':
            devtools.pprint(pipeline)

# TODO: add option to change input and output

