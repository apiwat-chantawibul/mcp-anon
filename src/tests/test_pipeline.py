from pathlib import Path
from tempfile import TemporaryFile

import pytest
import yaml

from app.pipeline import Pipeline


pipelines_directory = Path(__file__).parent / 'pipelines'


@pytest.fixture(scope = 'module')
def pipelines():
    return {
        path.stem: yaml.safe_load(path)
        for path in pipelines_directory.glob('*.yaml')
    }


@pytest.mark.parametrize(
    'path',
    tuple(pipelines_directory.glob('*.yaml')),
)
def test_pipeline_file_roundtrip(path):
    loaded = Pipeline.from_file(path)
    with TemporaryFile('w+') as f:
        loaded.to_file(f)
        f.seek(0)
        reloaded = Pipeline.from_file(f)
    assert loaded == reloaded

