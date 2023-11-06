from fastapi import FastAPI, Depends, WebSocket
import time
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.responses import RedirectResponse, FileResponse, Response, PlainTextResponse, StreamingResponse, JSONResponse, HTMLResponse
from fastapi.exceptions import ResponseValidationError, HTTPException
from sqlalchemy.ext.asyncio import create_async_engine
from dynamicdb.core.models.user_models import SQLModel, UserBase, UserCreate, UserRead, User
from dynamicdb.core.schemas.dynamic_generator_schemas import SqlModelGeneratorSchema
import socket
from sqlmodel import select
from typing import Any
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


def on_message(ws:WebSocket, message):
    time.sleep(1)
    print(f"Received message: {message}")
    ws.send("Hello, WebSocket!")

def on_error(ws:WebSocket, error):
    print(f"Error: {error}")

def on_close(ws:WebSocket, close_status_code, close_msg):
    print("Closed")

def on_open(ws:WebSocket):
    ws.send("Hello, WebSocket!")

@app.get("/")
async def hello_world():
    return {"message": "Hello World"}

@app.get("/getsocket", response_class=HTMLResponse)
async def get_websocket_html():
    return """
    <html>
    <head>
        <title>WebSocket Example</title>
    </head>
    <body>
        <h1>WebSocket Example</h1>
        <input type="text" id="message" placeholder="Enter a message">
        <button onclick="startWebSocket()">Start WebSocket</button>
        <button onclick="sendMessage()">Send</button>
        <div id="messages"></div>
        <script>
            var socket;
            var messageInterval;

            function startWebSocket() {
                if (socket === undefined || socket.readyState === WebSocket.CLOSED) {
                    socket = new WebSocket("ws://" + window.location.host + "/ws");

                    socket.onopen = function (event) {
                        document.getElementById("messages").innerHTML = "WebSocket connection opened";
                        messageInterval = setInterval(sendAutoMessage, 3000); // Send a message every 3 seconds
                    };

                    socket.onmessage = function (event) {
                        var messagesDiv = document.getElementById("messages");
                        messagesDiv.innerHTML += "<p>Received: " + event.data + "</p>";
                    };

                    socket.onclose = function (event) {
                        if (event.wasClean) {
                            console.log("WebSocket closed cleanly, code=" + event.code + " reason=" + event.reason);
                        } else {
                            console.error("WebSocket connection died");
                        }
                        clearInterval(messageInterval);
                    };

                    socket.onerror = function (error) {
                        console.error("WebSocket Error: " + error.message);
                        clearInterval(messageInterval);
                    };
                }
            }

            function sendMessage() {
                var messageInput = document.getElementById("message");
                var message = messageInput.value;
                if (socket.readyState === WebSocket.OPEN) {
                    socket.send(message);
                    messageInput.value = "";  // Clear the input field
                }
            }

            function sendAutoMessage() {
                if (socket.readyState === WebSocket.OPEN) {
                    socket.send("Automated message");
                }
            }
        </script>
    </body>
    </html>
    """


@app.post("/users/create")
async def create_user(user:UserCreate, db: AsyncSession = Depends(get_db))->UserRead:
    try:
        db_user = User.from_orm(user)
    except Exception as e:
        print(e)
        print([e])

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
        return JSONResponse({"error":"Non Existant Etity", "entity_values":{"user_id":user_id}})
    return user

@app.get("/users")
async def get_all_users(db: AsyncSession = Depends(get_db))->list[UserRead]:
    query = select(User)
    result = await db.execute(query)
    users = result.scalars().all()
    return users

@app.post("/create_table")
async def create_table(table_schema:SqlModelGeneratorSchema, db: AsyncSession = Depends(get_db))->SqlModelGeneratorSchema:
    return table_schema

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

if __name__ == "__main__":
    import uvicorn
    host = socket.gethostname()
    uvicorn.run(app, host=host, port=8000)

