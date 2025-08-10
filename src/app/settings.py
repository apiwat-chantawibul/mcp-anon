from pathlib import Path
from functools import cache

from pydantic import (
    Field,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for mcp-anon server"""
    # Takes value for environment variables only, not CLI arguments.
    # Because CLI command used is `fastmcp`, not a custom one.
    model_config = SettingsConfigDict(
        env_prefix = 'ANON_',
    )

    pipeline_dir: Path = Field(
        'pipeline',
        description = (
            'Location for pipeline files.'
            ' If running mcp-anon locally, mount client filesystem to this path to do collaborative edit.'
        ),
    )

    autopersist: bool = Field(
        True,
        description = 'Save application state to file on every update',
    )
    
    restore: bool = Field(
        True,
        description = 'Attempt to restore application state on initialization',
    )


@cache
def get_settings() -> Settings:
    return Settings()

