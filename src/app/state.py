from pathlib import Path
import shutil
from functools import cached_property

import pandas as pd
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.pipeline import Pipeline, Load, Transform, Export
from app.settings import get_settings
from app.dataset.view.schema import get_dataset_schema, DatasetSchema


class PipelineView(BaseModel):
    """Pipeline status report for client"""
    pipeline: Pipeline
    result_schema: DatasetSchema


class State(BaseModel):
    """Application state of mcp-anon server.

    - Keep cache of resulting dataset so pipeline does not need to be rerun on
      every request.
    """

    model_config = ConfigDict(arbitrary_types_allowed = True)

    # TODO: use xarray dataset to support multi-table dataset?
    pipeline: Pipeline = Pipeline()
    workdir: Path = Field(
        default_factory = lambda: get_settings().pipeline_dir,
        description = 'Where pipeline is stored on mcp-anon server',
    )

    @cached_property
    def original_dataset(self) -> pd.DataFrame:
        """Dataset after it is read from source"""
        if self.pipeline.load is None:
            raise Exception('Dataset not available because loader is not set.')
        return self.pipeline.load()

    @cached_property
    def result_dataset(self) -> pd.DataFrame:
        """Dataset after it is transformed"""
        return self.pipeline.transform(self.original_dataset.copy())

    def set_load(self, load: Load) -> None:
        if 'result_dataset' in self.__dict__:
            del self.result_dataset
        if 'original_dataset' in self.__dict__:
            del self.original_dataset
        self.pipeline.load = load

    # TODO: add option for showing source code
    def view_pipeline(self) -> PipelineView:
        return PipelineView(
            # NOTE: This give client back resolved CSV path on server.
            # This leak server's internal filesystem structure. Might want to change.
            pipeline = self.pipeline,
            result_schema = get_dataset_schema(self.result_dataset),
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

    def write_pipeline_code():
        """
        # Copy anonymization pipeline template files to working directory
        # TODO Copy static files used by pipeline into workdir
        # TODO handle existing files
        shutil.copytree(
            Path(__file__).parent / 'pipeline/template',
            self.workdir,
        )
        """
        # TODO write dynamic code to files according to self.pipeline
        raise NotImplementedError()

    def set_export(self, export: Export) -> None:
        self.pipeline.export = export

