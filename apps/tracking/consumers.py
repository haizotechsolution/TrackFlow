import json

from channels.generic.websocket import AsyncWebsocketConsumer


class TrackingConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.awb = self.scope['url_route']['kwargs']['awb']
        self.room_group_name = f'tracking_{self.awb}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def tracking_update(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))