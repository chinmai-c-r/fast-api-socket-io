from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import google.generativeai as genai
import socketio
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv(dotenv_path='.env')
app_url = os.environ.get('APP_URL')
gemini_key = os.environ.get('GEMINI_API_KEY')

if not app_url or not gemini_key:
    raise ValueError("environment variables GEMINI_API_KEY and APP_URL must be set")

genai.configure(api_key=gemini_key)

app = FastAPI()


@app.get("/")
def read_root():
    return {"data": "Api running"}

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=["http://localhost:3000","http://localhost:3001",app_url],  
)
app.mount("/socket.io", socketio.ASGIApp(socketio_server=sio))


@sio.event
async def connect(sid, environ):
    print(f"Client {sid} connected")


@sio.event
async def disconnect(sid):
    print(f"Client {sid} disconnected")

class UserMessage(BaseModel):
    text: str
    openai_key: str


@sio.event
async def user_message(sid, data):
    input_text = data["text"]
    
    print(f"Received message from {sid}: {input_text}")
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(input_text, stream=True)

        for chunk in response:  # Use a normal for loop
            if chunk.text:
                await sio.emit("chat_message", chunk.text, to=sid)
        
        await sio.emit("chat_message_end", {}, to=sid)
    
    except Exception as e:
        print(f"Error: {e}")
        await sio.emit("chat_message", "Sorry, there was an error processing your request.", to=sid)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)


