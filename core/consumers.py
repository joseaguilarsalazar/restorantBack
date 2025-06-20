from channels.generic.websocket import AsyncWebsocketConsumer
import json

class PedidoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join group
        await self.channel_layer.group_add("realtime_updates", self.channel_name)
        await self.accept()
        print("WebSocket connected:", self.channel_name)

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard("realtime_updates", self.channel_name)
        print("WebSocket disconnected:", self.channel_name)

    # This method name matches the "type" value from group_send
    async def send_data(self, event):
        # event["data"] is the list of pedidos we sent from the signal
        await self.send(text_data=json.dumps({
            "type": "pedido_update",
            "payload": event["data"]
        }))