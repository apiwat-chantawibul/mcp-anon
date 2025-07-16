from pathlib import Path
import shutil
from functools import cached_property

import pandas as pd
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.pipeline import Pipeline, Transform
from app.settings import get_settings


class State(BaseModel):
    """Application state of mcp-anon server.

    - Keep cache of resulting dataset so pipeline does not need to be rerun on
      every request.
    """

    model_config = ConfigDict(arbitrary_types_allowed = True)

    # TODO: use xarray dataset to support multi-table dataset?
    pipeline: Pipeline[pd.DataFrame] = Pipeline()
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

    def append_transform(self, transform: Transform) -> None:
        transform_sequence = self.pipeline.transform.sequence
        transform_sequence.append(transform)
        # TODO: do not clear, compute from current result
        # This might requires custom @property
        if hasattr(self, 'result_dataset'):
            del self.result_dataset

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

