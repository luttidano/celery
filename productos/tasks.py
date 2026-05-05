import time 
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .models import Producto

from decimal import Decimal
from pathlib import Path
from django.utils import timezone

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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
def generar_reporte_inventario_pdf():
    time.sleep(3)

    productos = list(Producto.objects.select_related('categoria').order_by('nombre'))
    total_unidades = sum(p.cantidad for p in productos)
    total_valor = sum((p.cantidad * p.precio) for p in productos) if productos else Decimal("0.00")

    reports_dir = Path(settings.REPORTS_DIR)
    reports_dir.mkdir(parents=True, exist_ok=True)

    filename = f"reporte_inventario_{timezone.now():%Y%m%d_%H%M%S}.pdf"
    file_path = reports_dir / filename

    pdf = canvas.Canvas(str(file_path), pagesize=letter)
    width, height = letter
    y = height - 50
    margin_x = 40

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(margin_x, y, "Reporte de inventario")
    y -= 18
    pdf.setFont("Helvetica", 10)
    pdf.drawString(margin_x, y, f"Generado: {timezone.now().strftime('%Y-%m-%d %H:%M')}")
    y -= 22

    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(margin_x, y, "SKU")
    pdf.drawString(margin_x + 90, y, "Nombre")
    pdf.drawString(margin_x + 350, y, "Cantidad")
    pdf.drawString(margin_x + 440, y, "Precio")
    y -= 14
    pdf.setFont("Helvetica", 10)

    for producto in productos:
        if y < 60:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(margin_x, y, "SKU")
            pdf.drawString(margin_x + 90, y, "Nombre")
            pdf.drawString(margin_x + 350, y, "Cantidad")
            pdf.drawString(margin_x + 440, y, "Precio")
            y -= 14
            pdf.setFont("Helvetica", 10)

        pdf.drawString(margin_x, y, producto.sku)
        pdf.drawString(margin_x + 90, y, producto.nombre[:32])
        pdf.drawRightString(margin_x + 400, y, str(producto.cantidad))
        pdf.drawRightString(margin_x + 520, y, f"${producto.precio}")
        y -= 14

    if y < 90:
        pdf.showPage()
        y = height - 50

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(margin_x, y, "Resumen")
    y -= 14
    pdf.setFont("Helvetica", 10)
    pdf.drawString(margin_x, y, f"Productos: {len(productos)}")
    y -= 12
    pdf.drawString(margin_x, y, f"Unidades: {total_unidades}")
    y -= 12
    pdf.drawString(margin_x, y, f"Valor total: ${total_valor}")

    pdf.showPage()
    pdf.save()

    return {"filename": filename}


