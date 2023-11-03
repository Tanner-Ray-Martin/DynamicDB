from fastapi import FastAPI, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.responses import RedirectResponse, FileResponse, Response, PlainTextResponse, StreamingResponse
from fastapi.exceptions import ResponseValidationError, HTTPException
from sqlalchemy.ext.asyncio import create_async_engine
from dynamicdb.core.models.user_models import SQLModel, UserBase, UserCreate, UserRead, User
import socket
from sqlmodel import select

DATABASE_URL = "sqlite+aiosqlite:///./data.db"

connect_args = {"check_same_thread": False}
engine = create_async_engine(DATABASE_URL, echo=True, connect_args=connect_args)

app = FastAPI()

async def get_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    db = AsyncSession(engine)
    try:
        yield db
    finally:
        await db.close()

@app.get("/")
async def hell_world():
    return {"message": "Hello World"}

@app.post("/users/create")
async def create_user(user:UserCreate, db: AsyncSession = Depends(get_db))->UserRead:
    db_user = User.from_orm(user)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@app.get("/users/{user_id}")
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db))->UserRead:
    query = select(User).filter_by(id=user_id)
    result = await db.execute(query)
    user = result.scalars().first()
    if not user:
        raise HTTPException(404, detail=f"No user with id: {user_id}")
    return user

@app.get("/users")
async def get_all_users(db: AsyncSession = Depends(get_db))->list[UserRead]:
    query = select(User)
    result = await db.execute(query)
    users = result.scalars().all()
    return users


if __name__ == "__main__":
    import uvicorn
    host = socket.gethostname()
    uvicorn.run(app, host=host, port=8000)

