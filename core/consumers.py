from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async

from .models import Pedido


class PedidoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("realtime_updates", self.channel_name)
        await self.accept()
        await self.send_initial_data()
        print("WebSocket connected:", self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("realtime_updates", self.channel_name)
        print("WebSocket disconnected:", self.channel_name)

    async def send_data(self, event):
        await self.send(text_data=json.dumps({
            "type": "pedido_update",
            "payload": event["data"]
        }))

    async def send_initial_data(self):
        data = await get_pedidos_data()
        await self.send(text_data=json.dumps({
            "type": "send_data",
            "data": data
        }))


@sync_to_async
def get_pedidos_data():
    pedidos = Pedido.objects.select_related('mesa', 'plato').exclude(estado="pagado")
    return [{
        'id': p.id,
        'mesa': p.mesa.id if p.mesa else None,
        'plato': p.plato.name if p.plato else None,
        'cantidad': p.cantidad,
        'datetime': p.fecha.isoformat(),
        'estado': p.estado
    } for p in pedidos]
