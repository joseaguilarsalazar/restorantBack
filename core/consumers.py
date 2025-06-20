from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from .models import Pedido

class PedidoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join group
        await self.channel_layer.group_add("realtime_updates", self.channel_name)
        await self.accept()
        # 📤 Send initial data on connect
        await self.send_initial_data()
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

    async def send_initial_data(self):
        pedidos = await sync_to_async(list)(Pedido.objects.exclude(estado="pagado"))
        data = [{
            'id': p.id,
            'mesa': p.mesa.id if p.mesa else None,
            'plato': p.plato.name if p.plato else None,
            'cantidad': p.cantidad,
            'datetime': p.fecha.isoformat(),
            'estado': p.estado
        } for p in pedidos]

        await self.send(text_data=json.dumps({
            "type": "send_data",
            "data": data
        }))