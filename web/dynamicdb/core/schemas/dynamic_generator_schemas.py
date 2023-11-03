from pydantic import BaseModel
from typing import Optional, Literal, Any
from datetime import date, datetime


allowed_dtypes = Literal["str", "int", "float", "date", "datetime", "bool"]


class SqlModelGeneratorField(BaseModel):
    """ if column field is not None then set any of these fields you need"""
    primary_key: bool = False
    unique: bool = False
    index: bool = False
    default_value: None | Any = None
    max_length: int | None = None
    min_length: int | None = None

class SqlModelGeneratorColumn(BaseModel):
    name:str
    colum_type:allowed_dtypes
    is_optional:bool
    column_field:SqlModelGeneratorField|None = None

class SqlModelGeneratorSchema(BaseModel):
    name:str
    all_columns: list[SqlModelGeneratorColumn]
    create_columns: list[SqlModelGeneratorColumn]
    read_columns:list[SqlModelGeneratorColumn]
    update_columns:list[SqlModelGeneratorColumn]
    delete_columns:list[SqlModelGeneratorColumn]