import pprint

import click
import devtools

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
    pprint.pprint(pipeline)


@cli.command()
@click.option(
    '--format', '-f', '_format',
    type = click.Choice([
        'json',
        'python-dict', 'pydict',
        'python-object', 'pyobj',
    ]),
    default = 'pydict',
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

