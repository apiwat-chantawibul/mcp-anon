from pathlib import Path
from tempfile import TemporaryFile

import pytest
import yaml
from pydantic import ValidationError

from mcp_anon.pipeline import Pipeline


# NOTE: I would love to use workdir fixture,
# but it is not available at test collection time.
pipelines_directory = Path(__file__).parent / 'workdir/pipelines'


@pytest.mark.parametrize(
    'path',
    tuple(pipelines_directory.glob('valid/*.yaml')),
)
def test_pipeline_file_roundtrip(path):
    loaded = Pipeline.from_file(path)
    with TemporaryFile('w+') as f:
        loaded.to_file(f)
        f.seek(0)
        reloaded = Pipeline.from_file(f)
    assert loaded == reloaded


@pytest.mark.parametrize(
    'path',
    tuple(pipelines_directory.glob('invalid/*.yaml')),
)
def test_invalid_pipeline_file(path):
    with pytest.raises(ValidationError):
        loaded = Pipeline.from_file(path)

