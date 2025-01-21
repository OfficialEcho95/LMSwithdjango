import asyncio
import socketio
import uvicorn
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import redirect, render
from LMS.models import User, Message
from django.contrib.auth.decorators import login_required
import json


# this is what runs the messaging function in the url
def socketio_info(request):
    # users = User.objects.all()
    users = User.objects.exclude(id=request.user.id)
    context = {"users": users}
    return render(request, "authentication/messages.html", context)


@login_required
def message_list(request):
    if request.method == "POST":

        data = json.loads(request.body)  # Parse the JSON body
        user_id = data.get("userId")

        if not user_id:
            return JsonResponse({"error": "User ID is required"}, status=400)

        # Fetch messages between the logged-in user and the selected user
        received_messages = Message.objects.filter(
            recipient=request.user, sender_id=user_id
        ).order_by("-timestamp")
        sent_messages = Message.objects.filter(
            sender=request.user, recipient_id=user_id
        ).order_by("-timestamp")

        # Prepare the message data to return as JSON
        messages = []
        for message in received_messages:
            messages.append(
                {
                    "sender": message.sender.username,
                    "content": message.content,
                    "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

        for message in sent_messages:
            messages.append(
                {
                    "sender": "You",
                    "content": message.content,
                    "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )

        # Sort messages by timestamp (ascending order)
        messages.sort(key=lambda x: x["timestamp"])

        return JsonResponse({"messages": messages})

    return JsonResponse({"error": "Invalid request method"}, status=400)


sio = socketio.AsyncServer(async_mode="asgi")
app = socketio.ASGIApp(sio)
message_queue = {}


@sync_to_async
def get_user_by_email(email):
    return get_user_model().objects.get(email=email)


def get_user_by_sid(sid):
    return get_user_model().objects.get(sid=sid)


@sync_to_async
def save_user_socket(user, sid):
    user.socket_id = sid
    user.save()


@sync_to_async
def clear_user_socket(user):
    user.socket_id = None
    user.save()


@sio.event
async def connect(request, sid, environ):  # use this guy as a view lets update this function
    user_email = environ.get("HTTP_USER_EMAIL")
    if user_email:
        try:
            user = await get_user_by_email(user_email)
            await save_user_socket(user, sid)
            print(f"User {user_email} connected with sid {sid}")
        except get_user_model().DoesNotExist:
            print(f"User {user_email} not found.")
    else:
        print("User email not provided in connection.")


@sio.event
async def disconnect(sid):
    try:
        user = await get_user_by_sid(sid)
        await clear_user_socket(user)
        print(f"User {user.email} disconnected.")
    except get_user_model().DoesNotExist:
        print(f"No user found with sid {sid}.")


@sio.event
async def send_message(sid, data):
    target_sid = data.get("target_sid")
    message = data.get("message")
    if target_sid in sio.manager.rooms["/"]:
        await sio.emit("message", {"message": message}, to=target_sid)
    else:
        print(f"Target {target_sid} not connected. Queuing message.")
        # messages would be added to database in a real-world application


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=7000)
