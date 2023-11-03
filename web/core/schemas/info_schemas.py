from pydantic import BaseModel
from typing import Literal

class TableUrls(BaseModel):
    table_name:str
    urls:list[str]

class TableUrlsResponse(BaseModel):
    table_urls:list[TableUrls]
    