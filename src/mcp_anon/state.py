from typing import Self
from pathlib import Path
import shutil
from functools import cached_property

import pandas as pd
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from mcp_anon.pipeline import Pipeline, Load, Transform, Export
from mcp_anon.settings import get_settings
from mcp_anon.dataset.view.schema import get_dataset_schema, DatasetSchema


class PipelineView(BaseModel):
    """Pipeline status report for client"""
    pipeline: Pipeline
    result_schema: DatasetSchema | None = Field(
        None,
        description = (
            'Dataset schema of current pipeline result.'
            ' Only available if loader stage is set and valid.'
        ),
    )
    warnings: list[str] | None = None


class LoaderNotSetException(Exception):
    def __init__(self, message = 'Dataset not available because loader is not set.'):
        super().__init__(message)


class State(BaseModel):
    """Application state of mcp-anon server.

    - Keep cache of resulting dataset so pipeline does not need to be rerun on
      every request.
    """

    model_config = ConfigDict(arbitrary_types_allowed = True)

    # TODO: use xarray dataset to support multi-table dataset?
    pipeline: Pipeline = Pipeline()
    pipeline_file: Path = Field(
        default_factory = lambda: get_settings().pipeline_file,
        description = 'Path to persist pipeline definition file.',
    )
    is_autopersist: bool = Field(
        default_factory = lambda: get_settings().autopersist,
    )

    @cached_property
    def original_dataset(self) -> pd.DataFrame:
        """Dataset after it is read from source"""
        if self.pipeline.load is None:
            raise LoaderNotSetException()
        return self.pipeline.load()

    @cached_property
    def result_dataset(self) -> pd.DataFrame:
        """Dataset after it is transformed"""
        return self.pipeline.transform(self.original_dataset.copy())

    def clear_all_cache(self):
        if 'result_dataset' in self.__dict__:
            del self.result_dataset
        if 'original_dataset' in self.__dict__:
            del self.original_dataset

    def set_load(self, load: Load) -> None:
        self.clear_all_cache()
        self.pipeline.load = load
        self.autopersist()

    # TODO: add option for showing source code
    def view_pipeline(self) -> PipelineView:
        warnings = []
        try:
            result_schema = get_dataset_schema(self.result_dataset)
        except Exception as e:
            warnings.append(f'Can not display schema of resulting dataset. {e}')
            result_schema = None
        return PipelineView(
            # NOTE: This give client back resolved CSV path on server.
            # This leak server's internal filesystem structure. Might want to change.
            pipeline = self.pipeline,
            result_schema = result_schema,
            warnings = warnings or None,
        )

    def append_transform(self, transform: Transform) -> None:
        """Append new transformation step and update app state.

        - Result_dataset will be updated immediately to ensure feedback on
          appending faulty transform.
        - New transform is only appended if it does not cause error.
        - All previous transforms must have already been tested.
          Otherwise, we will not know if error in the pipeline is caused by new
          transform or previously untested steps.
        """
        transform_sequence = self.pipeline.transform.sequence

        if 'result_dataset' in self.__dict__:
            self.result_dataset = transform(self.result_dataset)
            transform_sequence.append(transform)
        else:
            transform_sequence.append(transform)
            try:
                _ = self.result_dataset
            except Exception as e:
                transform_sequence.pop()
                raise e
            else:
                self.autopersist()

    def set_export(self, export: Export) -> None:
        self.pipeline.export = export
        self.autopersist()
    
    def persist(self) -> None:
        """Persist application state to file"""
        self.pipeline_file.parent.mkdir(parents = True, exist_ok = True)
        self.pipeline.to_file(self.pipeline_file)

    @classmethod
    def restore(cls) -> Self:
        """Restore application state from file"""
        return cls(
            pipeline = Pipeline.from_file(
                get_settings().pipeline_file
            ),
        )

    @classmethod
    def init(cls, restore = None) -> Self:
        if restore is None:
            restore = get_settings().restore
        if restore:
            try:
                return cls.restore()
            except Exception:
                pass
        return cls()

    def autopersist(self) -> None:
        if self.is_autopersist:
            self.persist()

    def clear_persisted(self) -> None:
        self.pipeline_file.unlink(missing_ok = True)
        
    def reset_pipeline(self) -> None:
        self.clear_all_cache()
        self.pipeline = Pipeline()
        self.clear_persisted()
