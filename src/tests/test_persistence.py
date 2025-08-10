import pytest
from fastmcp import Client

from app.server import app
from app.settings import get_settings
from tests.test_server import input_load_config


async def test_autopersist_and_restore(input_load_config):
    expected_empty_schema = {
        'pipeline': {
            'export': None,
            'load': None,
            'transform': {
                'sequence': [],
                'type': 'sequence',
            },
        },
        'result_schema': None,
    }
    expected_filled_schema = {
        'pipeline': {
            'export': None,
            'load': {
                'path': '/opt/app/src/tests/datasets/small.csv',
                'type': 'csv',
                },
            'transform': {
                'sequence': [{'fields': 'married', 'type': 'drop'}],
                'type': 'sequence',
                },
            },
        'result_schema': {
            'fields': [
                {'datatype': 'int64[pyarrow]', 'name': 'id'},
                {'datatype': 'string[pyarrow]', 'name': 'name'},
                {'datatype': 'int64[pyarrow]', 'name': 'salary'},
            ],
        },
    }
    results = {}
    async with Client(app) as client:
        app.state.clear_persisted()
        results['view_before_edit'] = await client.call_tool('pipeline_view')
        assert results['view_before_edit'].structured_content == expected_empty_schema

        results['view_after_edit'] = await client.call_tool('pipeline_view')
        results['set'] = await client.call_tool('loader_set', input_load_config)
        results['append'] = await client.call_tool('transformer_append', {
            'transform': {
                'type': 'drop',
                'fields': 'married',
            }
        })
        results['view_after_edit'] = await client.call_tool('pipeline_view')
        assert results['view_after_edit'].structured_content == expected_filled_schema

    async with Client(app) as client:
        results['view_after_restore'] = await client.call_tool('pipeline_view')
        assert results['view_after_restore'].structured_content == expected_filled_schema
        results['clear'] = await client.call_tool('pipeline_reset')
        assert results['clear'].structured_content == expected_empty_schema

    async with Client(app) as client:
        results['view_after_clear'] = await client.call_tool('pipeline_reset')
        assert results['view_after_clear'].structured_content == expected_empty_schema
        app.state.clear_persisted()

