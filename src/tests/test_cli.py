import json

import pytest
from click.testing import CliRunner

from mcp_anon.pipeline import Pipeline
from mcp_anon.pipeline.cli import cli


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


def test_run(outdir):
    runner = CliRunner()
    result = runner.invoke(cli, [
        'run',
        'pipelines/valid/simple.yaml',
    ])
    assert not result.exception
    outfile = outdir / 'small.csv'
    assert outfile.is_file()
    with open(outfile, 'r') as f:
        outcontent = f.readlines()
    expected_outcontent = [
        'id,name,salary,married\n',
        '101,alice,"(20000, 30000]",0\n',
        '102,bob,"(10000, 20000]",1\n',
    ]
    assert outcontent == expected_outcontent

