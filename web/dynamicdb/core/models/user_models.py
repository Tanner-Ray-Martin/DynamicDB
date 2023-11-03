from sqlmodel import Field, SQLModel
from typing import Optional, LiteralString

class UserBase(SQLModel):
    username: str = Field(max_length=50, unique=False, index=True, description="The username of the user")
    email: str = Field(max_length=100, unique=False, index=True, description="The email address of the user")
    full_name: str

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, description="the unique id of the user")

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int
