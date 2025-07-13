from pydantic import BaseModel
import pandas as pd


class FieldSchema(BaseModel):
    name: str
    datatype: str


class DatasetSchema(BaseModel):
    fields: list[FieldSchema]


def get_dataset_schema(df: pd.DataFrame) -> DatasetSchema:
    # TODO report type as string instead of object when possible
    # TODO try pyarrow dtype
    return DatasetSchema(
        fields = [
            {
                'name': col,
                'datatype': str(df[col].dtype),
            }
            for col in df
        ],
    )

