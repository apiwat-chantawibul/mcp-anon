from pydantic import BaseModel
import pandas as pd


class FieldSchema(BaseModel):
    name: str
    datatype: str


class DatasetSchema(BaseModel):
    fields: list[FieldSchema]


def get_dataset_schema(df: pd.DataFrame) -> DatasetSchema:
    return DatasetSchema(
        fields = [
            {
                'name': col,
                'datatype': repr(df[col].dtype),
            }
            for col in df
        ],
    )

