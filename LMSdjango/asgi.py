"""
ASGI config for LMSdjango project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application
import socketio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LMSdjango.settings')

from django.core.asgi import get_asgi_application

# Create a new Socket.IO server
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


# Wrap the default Django ASGI application with the Socket.IO app
django_asgi_app = get_asgi_application()
application = socketio.ASGIApp(sio, django_asgi_app, socketio_path='messages/socket.io')

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")


@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")
