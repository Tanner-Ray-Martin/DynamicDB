from pydantic import BaseModel
from datetime import datetime as DateTime

class ExistingInput(BaseModel):
    table_name:str
    created_by:str
    created_on:DateTime

class ExistingOutput(BaseModel):
    id:int
    table_name:str
    created_by:str
    created_on:DateTime