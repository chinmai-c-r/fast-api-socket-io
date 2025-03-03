from fastapi import FastAPI,Request
import socketio
from routers import users,chat


app = FastAPI()

@app.get("/")
def running():
    return {"data":"API running"}

app.mount("/socket.io", socketio.ASGIApp(socketio_server=chat.sio))
app.include_router(users.router)









