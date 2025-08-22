import json

import pytest
from click.testing import CliRunner

from app.pipeline import Pipeline
from app.pipeline.cli import cli


@pytest.mark.parametrize(
    'extra_args',
    [
        tuple(),
        ('--format', 'python-dict'),
        ('--format', 'pyobj'),
    ],
)
def test_inspect_pretty(extra_args):
    runner = CliRunner()
    result = runner.invoke(cli, [
        'inspect',
        'pipelines/valid/simple.yaml',
        *extra_args,
    ])
    # For pretty formats, just do a smoke test
    assert not result.exception


def test_inspect_json():
    runner = CliRunner()
    result = runner.invoke(cli, [
        'inspect',
        'pipelines/valid/simple.yaml',
        '--format',
        'json',
    ])
    assert not result.exception
    # For JSON inspection, output must be a valid JSON
    from_json = Pipeline.model_validate(json.loads(result.stdout))

