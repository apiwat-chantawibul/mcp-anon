from __future__ import annotations
import ast
from typing import Callable, Literal
import inspect

from pydantic import (
    Field,
    model_validator,
    PrivateAttr,
)

from .step import Transform


class CustomTransform[Dataset](Transform[Dataset]):
    """Transformation dataset defined by arbitrary python code."""

    type: Literal['custom'] = 'custom'
    function_definition: str = Field(
        description = inspect.cleandoc("""
            Must take a dataset and return the transformed dataset.
            For example,

            ```
            def drop_name(df: pd.DataFrame) -> pd.DataFrame:
                return df.drop(columns = 'name')
            ```
        """),
    )
    _function: Callable[[Dataset], Dataset] = PrivateAttr()

    @model_validator(mode = 'after')
    def validate_function_definition(self) -> CustomTransform:
        try:
            parsed = ast.parse(self.function_definition)
        except SyntaxError as e:
            raise ValueError(f"Invalid syntax in function definition: {e}") from e

        match parsed.body:
            case [ast.FunctionDef() as func_def]:
                pass
            case _:
                raise ValueError('custom code must be single function definition')

        # TODO: validate function signature
        code_object = compile(parsed, filename='<string>', mode='exec')
        namespace = {}
        exec(code_object, namespace)
        self._function = namespace[func_def.name]
        return self

    def __call__(self, ds: Dataset) -> Dataset:
        return self._function(ds)

