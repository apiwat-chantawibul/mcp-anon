from pathlib import Path
import inspect

import pytest
from fastmcp import FastMCP, Client

from app.server import app, LoaderConfig


async def test_describe_initial():
    async with Client(app) as client:
        result = await client.call_tool('loader_describe')
        assert result.data is None


@pytest.fixture
def input_load_config():
    return {
        'loader_config': {
            'type': 'csv',
            'path': str(Path(__file__).parent / 'datasets/small.csv'),
        },
    }


async def test_load_and_describe(input_load_config):
    results = {}
    async with Client(app) as client:
        results['set'] = await client.call_tool('loader_set', input_load_config)
        results['describe'] = await client.call_tool('loader_describe')
        reflected_load_config = results['describe'].data
        assert input_load_config['loader_config'] == reflected_load_config


async def test_missing_load_type(input_load_config):
    del input_load_config['loader_config']['type']
    async with Client(app) as client:
        with pytest.raises(Exception):
            result = await client.call_tool('loader_set', input_load_config)


async def test_original_view_schema(input_load_config):
    expected_schema = {'fields': [
        {'name': 'id', 'datatype': 'int64[pyarrow]'},
        {'name': 'name', 'datatype': 'string[pyarrow]'},
        {'name': 'salary', 'datatype': 'int64[pyarrow]'},
        {'name': 'married', 'datatype': 'int64[pyarrow]'},
    ]}
    results = {}
    async with Client(app) as client:
        results['set'] = await client.call_tool('loader_set', input_load_config)
        assert results['set'].structured_content == expected_schema
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
        results['set'] = await client.call_tool('loader_set', input_load_config)
        results['original_stats'] = await client.call_tool('original_view_stats')
        assert results['original_stats'].structured_content == expected_stats


async def test_custom_transform(input_load_config):
    code = inspect.cleandoc("""
        def remove_salary_and_reset_id(df):
            df = df.drop(columns = 'salary')
            df['id'] = df.index
            return df
    """)
    expected_stats = {
        'id': {'25%': 0.25,
               '50%': 0.5,
               '75%': 0.75,
               'count': 2.0,
               'max': 1.0,
               'mean': 0.5,
               'min': 0.0,
               'std': 0.7071067811865476},
        'married': {'25%': 0.25,
                    '50%': 0.5,
                    '75%': 0.75,
                    'count': 2.0,
                    'max': 1.0,
                    'mean': 0.5,
                    'min': 0.0,
                    'std': 0.7071067811865476}}
    results = {}
    async with Client(app) as client:
        results['set'] = await client.call_tool('loader_set', input_load_config)
        results['append'] = await client.call_tool('transformer_append', {
            'transform': {
                'type': 'custom',
                'function_definition': code,
            }
        })
        results['stats'] = await client.call_tool('result_view_stats')
        assert results['stats'].structured_content == expected_stats
        results['view'] = await client.call_tool('transformer_view')
        assert results['view'].structured_content == {
            'type': 'sequence',
            'sequence': [
                {
                    'function_definition': code,
                    'type': 'custom',
                },
            ],
        }


async def test_bin_transform(input_load_config):
    expected_schema = {'fields': [
        {'name': 'id', 'datatype': 'int64[pyarrow]'},
        {'name': 'name', 'datatype': 'string[pyarrow]'},
        {'name': 'salary', 'datatype': 'category'},
        {'name': 'married', 'datatype': 'int64[pyarrow]'},
    ]}
    results = {}
    async with Client(app) as client:
        results['set'] = await client.call_tool('loader_set', input_load_config)
        results['append'] = await client.call_tool('transformer_append', {
            'transform': {
                'type': 'bin',
                'input_field': 'salary',
                'bins': [0, 10000, 20000, 30000],
            }
        })
        results['result_schema'] = await client.call_tool('result_view_schema')
        assert results['result_schema'].structured_content == expected_schema
        # TODO: This test is dictating implementation too much.
        # However, we are missing a way to confirm change without direct app.state access.
        interval = app.state.result_dataset.salary[0]
        assert (interval.left, interval.right) == (20000, 30000)


async def test_drop_transform(input_load_config):
    expected_schema = {'fields': [
        {'name': 'salary', 'datatype': 'int64[pyarrow]'},
        {'name': 'married', 'datatype': 'int64[pyarrow]'},
    ]}
    results = {}
    async with Client(app) as client:
        results['set'] = await client.call_tool('loader_set', input_load_config)
        results['append'] = await client.call_tool('transformer_append', {
            'transform': {
                'type': 'drop',
                'fields': ['id', 'name'],
            }
        })
        results['result_schema'] = await client.call_tool('result_view_schema')
        assert results['result_schema'].structured_content == expected_schema


async def test_drop_non_existent_field(input_load_config):
    results = {}
    async with Client(app) as client:
        results['set'] = await client.call_tool('loader_set', input_load_config)
        with pytest.raises(Exception, match = 'non_existent'):
            results['append'] = await client.call_tool('transformer_append', {
                'transform': {
                    'type': 'drop',
                    'fields': 'non_existent',
                }
            })

