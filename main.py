from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from openai import OpenAI
import socketio
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env.prod')
openai_api_key = os.getenv("OPENAI_KEY")
app_url = os.getenv("APP_URL")


if not openai_api_key or not app_url:
    raise ValueError("environment variables OPENAI_KEY and APP_URL must be set")

app = FastAPI()

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=["http://localhost:3000","https://chinmai.vercel.app/"],  
)
app.mount("/socket.io", socketio.ASGIApp(socketio_server=sio))


client = OpenAI(
    api_key=openai_api_key
)


@sio.event
async def connect(sid, environ):
    print(f"Client {sid} connected")


@sio.event
async def disconnect(sid):
    print(f"Client {sid} disconnected")


@sio.event
async def user_message(sid, data):
    print(f"Received message from {sid}: {data}")
    try:
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": data},
            ],
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                await sio.emit("chat_message", content, to=sid)

        await sio.emit("chat_message_end", {}, to=sid)

    except Exception as e:
        print(f"Error: {e}")
        await sio.emit(
            "chat_message",
            "Sorry, there was an error processing your request.",
            to=sid,
        )


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)


