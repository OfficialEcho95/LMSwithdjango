import asyncio
import socketio
from socketio.exceptions import TimeoutError

sio = socketio.AsyncClient()
connected_users = {}  # To store connected users


@sio.event
async def connect():
    print("Connected, session ID:", sio.sid)


@sio.event
async def disconnect():
    print("Disconnected from the server.")


@sio.event
async def message(data):
    print("Message received:", data)


async def send_message(target_sid, message):
    await sio.emit("send_message", {"target_sid": target_sid, "message": message})


@sio.event
async def user_list(data):
    global connected_users
    connected_users = data
    print("Connected users:", connected_users)


@sio.event
async def notification(data):
    print("Notification received:", data)


async def main():
    try:
        await sio.connect(
            "http://localhost:7000/messages/socket.io", transports=["websocket"]
        )
        print("Connected, session ID:", sio.sid)

        print("Connected users:", connected_users)
        target_sid = input("Enter the session ID of the target user: ")
        message = input("Enter a message to send to the target: ")
        await send_message(target_sid, message)

        await sio.emit("notification", {"alert": "You have a new notification!"})

        await sio.wait()  # Wait for events from the server
    except Exception as e:
        print("Error:", str(e))
    finally:
        await sio.disconnect()
        print("Disconnected")


asyncio.run(main())
