from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Pedido
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import time

# Shared memory cache
last_sent_time = 0
DEBOUNCE_SECONDS = 0.5 # send at most twice per second

@receiver([post_save, post_delete], sender=Pedido)
def notify_clients_on_change(sender, instance, **kwargs):
    global last_sent_time
    now = time.time()

    if now - last_sent_time < DEBOUNCE_SECONDS:
        return  # skip this signal, it's too soon

    last_sent_time = now

    channel_layer = get_channel_layer()
    pedidos = Pedido.objects.exclude(estado='pagado')
    data = [{
        'id': p.id,
        'mesa': p.mesa.id if p.mesa else None,
        'plato': p.plato.name if p.plato else None,
        'cantidad': p.cantidad,
        'datetime': p.fecha.isoformat(),
        'estado': p.estado
    } for p in pedidos]

    async_to_sync(channel_layer.group_send)(
        "realtime_updates",
        {"type": "send_data", "data": data}
    )