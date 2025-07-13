from pathlib import Path

import pytest
from fastmcp import FastMCP, Client

from app.server import app
from app.pipeline.pandas.load import LoadCsv


async def test_describe_initial():
    async with Client(app) as client:
        result = await client.call_tool('loader_describe')
        assert result.data is None


@pytest.fixture(scope = 'module')
def input_load_config():
    return LoadCsv(
        type = 'csv',
        path = Path(__file__).parent / 'datasets/small.csv',
    )


async def test_load_and_describe(input_load_config):
    results = {}
    async with Client(app) as client:
        results['set'] = await client.call_tool('loader_set', {
            'load': input_load_config
        })
        assert results['set'].data is None
        results['describe'] = await client.call_tool('loader_describe')
        reflected_load_config = LoadCsv(**results['describe'].data)
        assert input_load_config == reflected_load_config


async def test_original_view_schema(input_load_config):
    expected_schema = {'fields': [
        {'name': 'id', 'datatype': 'int64'},
        {'name': 'name', 'datatype': 'object'},
        {'name': 'salary', 'datatype': 'int64'},
        {'name': 'married', 'datatype': 'int64'},
    ]}
    results = {}
    async with Client(app) as client:
        results['set'] = await client.call_tool('loader_set', {
            'load': input_load_config
        })
        results['original_schema'] = await client.call_tool('original_view_schema')
        assert results['original_schema'].structured_content == expected_schema
        results['result_schema'] = await client.call_tool('result_view_schema')
        assert results['result_schema'].structured_content == expected_schema


async def test_original_view_stats(input_load_config):
    expected_stats = {
        'id': {'25%': 101.25,
               '50%': 101.5,
               '75%': 101.75,
               'count': 2.0,
               'max': 102.0,
               'mean': 101.5,
               'min': 101.0,
               'std': 0.7071067811865476},
        'married': {'25%': 0.25,
                    '50%': 0.5,
                    '75%': 0.75,
                    'count': 2.0,
                    'max': 1.0,
                    'mean': 0.5,
                    'min': 0.0,
                    'std': 0.7071067811865476},
        'salary': {'25%': 18750.0,
                   '50%': 22500.0,
                   '75%': 26250.0,
                   'count': 2.0,
                   'max': 30000.0,
                   'mean': 22500.0,
                   'min': 15000.0,
                   'std': 10606.601717798212}}
    results = {}
    async with Client(app) as client:
        results['set'] = await client.call_tool('loader_set', {
            'load': input_load_config
        })
        results['original_stats'] = await client.call_tool('original_view_stats')
        assert results['original_stats'].structured_content == expected_stats

