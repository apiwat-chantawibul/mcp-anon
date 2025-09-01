from contextlib import contextmanager

import pytest
from fastmcp import Client

from app.server import app
from app.settings import get_settings


@contextmanager
def use_pipeline_file(pipeline_file):
    settings = get_settings()
    original = settings.model_copy()
    settings.autopersist = False
    settings.pipeline_file = pipeline_file
    yield
    settings.autopersist = original.autopersist
    settings.pipeline_file = original.pipeline_file


@pytest.mark.parametrize(
    'pipeline_file',
    [
        'pipelines/valid/no-loader.yaml',
        'pipelines/valid/empty.yaml',
    ],
)
async def test_view_pipeline_without_loader(pipeline_file):
    with use_pipeline_file(pipeline_file):
        async with Client(app) as client:
            result = await client.call_tool('pipeline_view')
            warnings = result.structured_content['warnings'] or []
            assert any('loader is not set' in x for x in warnings)


async def test_view_pipeline_with_transform_error():
    # Drop non-existent column
    pass

