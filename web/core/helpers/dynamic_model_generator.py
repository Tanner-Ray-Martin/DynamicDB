from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Table, Boolean
from sqlalchemy.orm import DeclarativeBase
# Example usage:
from pydantic import create_model, BaseModel
from datetime import datetime as dt
from datetime import date as dtDate
from typing import Any
from core.schemas.generator_schemas import SchemaGenSchema, SqlGenSchema
from core.models.foundation import Base
from random import randint, choice, uniform
from pydantic import StringConstraints, StrictStr
import os
this_file_path = __file__
this_file_path_list = os.path.splitroot(this_file_path)
this_file_name = os.path.basename(this_file_path)
this_file_dir = os.path.dirname(this_file_path)
this_file_dir_name = os.path.basename(this_file_dir)
this_file_dir_list = os.path.split(this_file_dir)
core_dir = this_file_dir_list[0]
models_dir = os.path.join(core_dir, 'models')
schemas_dir = os.path.join(core_dir, 'schemas')
user_generated_models_path = os.path.join(models_dir, "user_generated_models.py")
user_generated_schemas_path = os.path.join(schemas_dir, "user_generated_schemas.py")


def save_model_code(code:str):
    with open(user_generated_models_path, 'r') as fp:
        existing_code = fp.read()
    new_code = existing_code + "\n" + code
    with open(user_generated_models_path, 'w') as fp:
        fp.write(new_code)

def save_pydantic_schema_code(code:str):
    with open(user_generated_schemas_path, 'r') as fp:
        existing_code = fp.read()
    new_code = existing_code + "\n" + code
    with open(user_generated_schemas_path, 'w') as fp:
        fp.write(new_code)

def generate_sqlalchemy_model_code(model_class):
    """
    Generate Python code from an SQLAlchemy Base model class and save it to a file.
    
    Args:
        model_class: SQLAlchemy Base model class.
        output_file: File path to save the generated code.
    """
    # Get the table name and column information from the model class
    table_name = model_class.__table__.name
    columns = model_class.__table__.columns

    # Generate Python code
    code = f"class {model_class.__name__}(Base):\n"
    code += f'    __tablename__ = "{table_name}"\n\n'

    for column in columns:
        column_name = column.name
        column_type = column.type
        code += f'    {column_name} = Column({column_type}, primary_key={column.primary_key}, index={column.index})\n'

    return code

def pydantic_model_to_sql_database2(pydantic_model:BaseModel, table_name: str, meta_data):
    cls_name = table_name.title().strip().replace(" ", "")
    table_name = table_name.lower().strip().replace(" ", "_")
    table = Table(table_name, meta_data)
    
def pydantic_model_to_sql_database(pydantic_model:BaseModel, table_name: str):
    print(table_name)
    
    cls_name = table_name.replace("_schema", "_db").title().replace(" ", "")
    table_name = cls_name.lower()
    """
    my user generated database
    myusergenerateddatabase
    my_user_generated_database
    my_user_generated_databasedb
    my_user_generated_databasedb
    """
    class_dict = {
        "__tablename__": table_name,
        "id": Column(Integer, primary_key=True, index=True)
    }
    MyNewClass = type(cls_name, (Base,), class_dict)

    for field_name, field_type in pydantic_model.__annotations__.items():
        if field_type == str or field_type == 'str':
            setattr(MyNewClass, field_name, Column(String))
        elif field_type == float or field_type == 'float':
            setattr(MyNewClass, field_name, Column(Float))
        elif field_type == int or field_type == 'int':
            setattr(MyNewClass, field_name, Column(Integer))
        elif field_type == DateTime or field_type == dt:
            setattr(MyNewClass, field_name, Column(DateTime))
        elif field_type == Date or field_type == dtDate:
            setattr(MyNewClass, field_name, Column(Date))
        elif field_type == bool or field_type == 'bool':
            setattr(MyNewClass, field_name, Column(Boolean))
        else:
            print("field type not handled", [field_type], [field_name])
    
    return MyNewClass

def python_dictionary_to_pydantic_model(name: str, dict_def: dict[str, Any]):
    fields = {}
    for field_name, value in dict_def.items():
        if isinstance(value, str):
            if value == "Date":
                value = dtDate
            elif value == "DateTime":
                value = dt
            fields[field_name] = (value, ...)
    return create_model(name, **fields)

def pydantic_model_to_code(model_class):
    if not issubclass(model_class, BaseModel):
        raise ValueError("Input class must be a Pydantic model.")

    model_code = f"class {model_class.__name__}(BaseModel):\n"

    for field_name, field_info in model_class.__annotations__.items():
        field_type = field_info.__name__
        default_value = getattr(model_class, field_name, None)
        field_declaration = f"    {field_name}: {field_type}"

        if default_value is not None:
            default_value_repr = repr(default_value)
            field_declaration += f" = {default_value_repr}"

        field_declaration += "\n"
        model_code += field_declaration

    return model_code

def construct_schema_template(schema:BaseModel)->BaseModel:
    field_data = schema.model_fields
    schema_template = {}
    string_choices = ["My Value", "Wachter, Inc", "Rollout", "Hello World", "Created using Python", "Created using SqlAlchemy", "Created using Pydantic", "Created using FastApi"]
    annotation_types = []
    for key, field_info in field_data.items():
        annotation_type = field_info.annotation
        if annotation_type == str:
            schema_template.update({key:choice(string_choices)})
        elif annotation_type == int:
            schema_template.update({key:randint(-10000, 10000)})
        elif annotation_type == float:
            schema_template.update({key:uniform(-10000.00, 10000.00)})
        elif annotation_type == dtDate:
            schema_template.update({key:dtDate.today()})
        elif annotation_type == dt:
            schema_template.update({key:dt.now()})
        elif annotation_type == bool:
            schema_template.update({key:choice([True, False])})
        annotation_types.append(annotation_type)
    
    schema_from_template = schema(**schema_template)
    return schema_from_template

def pydantic_schema_to_pydantic_schema(schema_generator_schema:SchemaGenSchema)->BaseModel:
    schema_name = schema_generator_schema.schema_name
    schema_name = schema_name.title()
    schema_name = schema_name.replace(" ", "")
    schema_name = schema_name + '_schema'
    dtype_conversion = {"str": str, "int":int, "float":float, "bool":bool, "Date":dtDate, "DateTime":dt}
    generated_fields:dict[str, tuple[Any, Any|ellipsis]] = {}
    fields = schema_generator_schema.schema_fields
    for field in fields:
        field_name = field.name
        default = field.default
        if not default and not isinstance(default, (int, float)):
            default = ...

        string_data_type = field.data_type
        data_type = dtype_conversion.get(string_data_type)
        generated_fields[field_name] = (data_type, default)
    
    return create_model(schema_name, **generated_fields)
