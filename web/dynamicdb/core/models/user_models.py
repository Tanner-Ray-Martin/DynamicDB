from sqlmodel import Field, SQLModel
from typing import Optional

class UserBase(SQLModel):
    username: str = Field(max_length=50, unique=False, index=True)
    email: str = Field(max_length=100, unique=False, index=True)
    full_name: str

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int
