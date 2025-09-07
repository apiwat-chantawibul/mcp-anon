from contextlib import contextmanager

import pytest
from fastmcp import Client

from mcp_anon.server import app
from mcp_anon.settings import get_settings


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
    with use_pipeline_file('pipelines/valid/drop-non-existent-column.yaml'):
        async with Client(app) as client:
            result = await client.call_tool('pipeline_view')
            warnings = result.structured_content['warnings'] or []
            assert any(
                (
                    'Can not display schema of resulting dataset' in x
                    and 'unknown_field' in x
                )
                for x in warnings
            )


async def test_mask_transform():
    with use_pipeline_file('pipelines/valid/mask-transform.yaml'):
        async with Client(app) as client:
            result = await client.call_tool('pipeline_view')
            assert list(app.state.result_dataset['name']) == ['a****', 'b*b']

