from fastapi import FastAPI
import socket
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}



if __name__ == "__main__":
    import uvicorn
    host = socket.gethostname()
    uvicorn.run(app, host=host, port=8000)

    