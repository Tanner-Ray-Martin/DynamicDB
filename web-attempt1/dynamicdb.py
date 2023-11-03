
import socket
#from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from fastapi import FastAPI, Depends
from dynamicdb.core.models.foundation import Base
from dynamicdb.core.models.existing_models import *
from dynamicdb.core.models.user_generated_models import *
from dynamicdb.core.models.existing_models import *
from dynamicdb.core.helpers import dynamic_model_generator
from dynamicdb.core.schemas.generator_schemas import SchemaGenSchema
from dynamicdb.core.schemas.info_schemas import TableUrlsResponse, TableUrls
# Create an SQLAlchemy engine and session
engine = create_async_engine(
    "sqlite+aiosqlite:///db4.sqlite3", connect_args={"check_same_thread": False}
)

SessionLocal = async_sessionmaker(engine)

# Create the database tables

async def get_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()


app = FastAPI()


@app.get("/")
async def groot_root(db: AsyncSession = Depends(get_db)):
    return {"Hello":"World"}

@app.get("/api/info/tableinfo/table_names")
async def groot_root(db: AsyncSession = Depends(get_db)):
    table_names:list[str] = [i for i in Base.metadata.tables.keys()]
    return {"table_names":table_names}

@app.get("/api/info/tableinfo/table_urls")
async def get_table_urls(db: AsyncSession = Depends(get_db))->TableUrlsResponse:
    table_endpoints = ["create", "read", "update", "delete"]
    prefix = "/api/tables"
    table_urls:list[TableUrls] = []
    for table_name in Base.metadata.tables.keys():
        urls:list[str] = []
        for table_endpoint in table_endpoints:
            table_endpoint_url = f"{prefix}/{table_name}/{table_endpoint}"
            urls.append(table_endpoint_url)
        
        table_urls.append(TableUrls(table_name=table_name, urls=urls))
    
    
    return TableUrlsResponse(table_urls=table_urls).model_dump()


@app.post("/api/auto_gen/generate/table")
async def create_database(payload:SchemaGenSchema, db: AsyncSession = Depends(get_db)):
    try:
        new_schema_model = dynamic_model_generator.pydantic_schema_to_pydantic_schema(payload)
        new_schema_object = dynamic_model_generator.construct_schema_template(new_schema_model)
        new_schema_code = dynamic_model_generator.pydantic_model_to_code(new_schema_model)
    except Exception as e:
        return {"error": str(e)}
    try:
        new_sql_model_database = dynamic_model_generator.pydantic_model_to_sql_database(new_schema_model, payload.schema_name)
        new_sql_model_code = dynamic_model_generator.generate_sqlalchemy_model_code(new_sql_model_database)
    except Exception as e:
        return {"error": str(e)}

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    dynamic_model_generator.save_model_code(new_sql_model_code)
    dynamic_model_generator.save_pydantic_schema_code(new_schema_code)
    new_sql_object = new_sql_model_database(**new_schema_object.model_dump())
    new_schema_model(**new_sql_object.__dict__)
    db.add(new_sql_object)
    await db.commit()
    await db.refresh(new_sql_object)
    return new_schema_model(**new_sql_object.__dict__)

if __name__ == "__main__":
    import uvicorn
    host = socket.gethostname()
    uvicorn.run(app, host=host, port=8000)
