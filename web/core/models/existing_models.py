from sqlalchemy import Column, Integer, String, Boolean, DateTime
from .foundation import Base

class Existing(Base):
    __tablename__ = "existing"
    id = Column(Integer, primary_key=True)
    table_name = Column(String, unique=True)
    created_by = Column(String)
    created_on = Column(DateTime)