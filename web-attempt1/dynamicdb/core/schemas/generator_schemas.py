from pydantic import BaseModel, constr, StringConstraints
from datetime import datetime as DateTime
from datetime import date as Date
from typing import Literal, Any

string_constraints = StringConstraints(pattern=r"^[a-zA-Z\s]+$")
data_types = Literal["str", "int", "float", "bool", "Date", "DateTime"]


class SchemaName(BaseModel):
    value: constr(pattern=r"^[a-zA-Z\s]+$")

class SchemaGenFields(BaseModel):
    name: str
    default: Any | None = None
    data_type: data_types


class SchemaGenSchema(BaseModel):
    schema_name: str
    schema_fields: list[SchemaGenFields]


class SqlGenFields(BaseModel):
    name: str
    data_type: data_types
    primary_key: bool = False
    default: Any | None = None
    unique: bool = False


class SqlGenSchema(BaseModel):
    tablename: str
    table_fields: list[SqlGenFields]


class SchemaGenResponse(BaseModel):
    structure: dict[str, Any]
    generated_template: dict[str, Any]