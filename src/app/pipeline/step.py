from typing import Literal
from abc import ABC, abstractmethod
from collections.abc import Callable
import inspect

from pydantic import (
    BaseModel,
    Field,
)


class Step[Dataset](BaseModel, Callable, ABC):
    """Step in pipeline"""

    type: str = Field(
        description = (
            'Discriminator between different step types.'
            ' Only unique within its own load/tranform/export category.'
        ),
    )

    @property
    def get_source_code(self) -> str:
        # TODO: check if this source code is in a form that
        # can be exported to 1. file 2. LLM prompt
        return inspect.getsource(self.__call__)


class Load[Dataset](Step[Dataset]):
    """Step that import raw data into pipeline"""

    @abstractmethod
    def __call__(self) -> Dataset:
        ...


class Transform[Dataset](Step[Dataset]):
    """Step in pipeline that transforms dataset."""

    @abstractmethod
    def __call__(self, ds: Dataset) -> Dataset:
        ...


class Export[Dataset](Step[Dataset]):
    """Step that export processed dataset"""

    @abstractmethod
    def __call__(self, ds: Dataset) -> None:
        ...

