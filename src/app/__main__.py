from enum import StrEnum

from pydantic_settings import BaseSettings, SettingsConfigDict

from .server import app


class TransportEnum(StrEnum):
    stdio = 'stdio'
    http = 'http'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        cli_parse_args = True,
        env_prefix = 'ANON_'
    )

    # HTTP transport specific settings are managed by FASTMCP_* env vars
    # See fastmcp.settings.Settings class
    transport: TransportEnum = 'stdio'


if __name__ == '__main__':
    settings = Settings()
    app.run(**settings.model_dump())

