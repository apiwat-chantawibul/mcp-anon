from typing import Literal
from pathlib import Path

from pydantic import (
    BaseModel,
    Field,
)
import pandas as pd
import sqlalchemy as sa

from ..step import Load


class LoadCsv(Load[pd.DataFrame]):
    """Load data from CSV file"""
    type: Literal['csv'] = 'csv'
    path: Path

    def __call__(self) -> pd.DataFrame:
        return pd.read_csv(
            self.path,
            dtype_backend = 'pyarrow',
        )


class LoadSql(Load[pd.DataFrame]):
    """Load data by executing SQL against a database connection.

    Connection parameters as defined by sqlalchemy.engine.URL.create()
    """
    type: Literal['sql'] = 'sql'
    sql: str = Field(
        examples = ['SELECT * FROM table'],
    )
    drivername: str = Field(
        examples = [
            'postgresql',
            'mysql',
            'sqlite',
        ],
    )
    host: str | None = Field(
        None,
        examples = [
            'localhost',
            '127.0.0.1',
        ],
    )
    port: int | None = Field(
        None,
        examples = [5432, 3306],
    )
    database: str | None = None
    username: str | None = None
    password: str | None = None

    def __call__(self) -> pd.DataFrame:
        connection_url = sa.engine.URL.create(**config)
        engine = sa.create_engine(connection_url)
        with engine.connect() as connection:
            df = pd.read_sql(
                sql,
                connection,
                dtype_backend = 'pyarrow',
            )

