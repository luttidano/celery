import time 
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .models import Producto


@shared_task
def notificar_stock_bajo(producto_id):
    time.sleep(2)
    producto = Producto.objects.filter(pk=producto_id).first()
    if not producto:
        return {"status": "not_found"}

    threshold = getattr(settings, "LOW_STOCK_THRESHOLD", 10)
    if producto.cantidad > threshold:
        return {"status": "skipped", "cantidad": producto.cantidad}

    subject = f"Stock bajo: {producto.nombre} ({producto.sku})"
    message = (
        f"El producto '{producto.nombre}' tiene {producto.cantidad} unidades. "
        f"Umbral: {threshold}."
    )
    recipients = getattr(settings, "LOW_STOCK_EMAIL_TO", [])
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "notificaciones@inventario.local")

    send_mail(subject, message, from_email, recipients)
    return {"status": "sent", "producto_id": producto.id, "cantidad": producto.cantidad}

@shared_task
def tarea_larga_duracion():
    print("Iniciando tarea de larga duración...")
    time.sleep(10)  # Simula una tarea que tarda 10 segundos
    print("Tarea de larga duración completada.")
    return "Resultado de la tarea"

