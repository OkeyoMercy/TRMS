from channels.generic.websocket import AsyncWebsocketConsumer
import json

class DriverConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.group_name = 'drivers'

        # Check if the user is authenticated and has the 'is_driver' attribute set to True
        if self.user.is_authenticated and getattr(self.user, 'is_driver', False):
            # Add this connection to the group
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        # Remove this connection from the group
        if self.user.is_authenticated and getattr(self.user, 'is_driver', False):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to the group, ensuring only authenticated drivers in the group receive it
        if self.user.is_authenticated and getattr(self.user, 'is_driver', False):
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'driver_message',
                    'message': message
                }
            )

    # Handle messages sent to the group
    async def driver_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
