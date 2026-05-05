from django.contrib import messages
from django.db.models import Count, ProtectedError, Sum
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from pathlib import Path
from celery.result import AsyncResult
from django.conf import settings
from django.urls import reverse

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .tasks import tarea_larga_duracion, notificar_stock_bajo, generar_reporte_inventario_pdf


from .forms import CategoriaForm, ProductoForm
from .models import Categoria, Producto


def producto_list(request):
	productos = Producto.objects.select_related('categoria').all()
	stock_total = Producto.objects.aggregate(total=Sum('cantidad')).get('total') or 0
	total_categorias_activas = Categoria.objects.filter(activa=True).count()
	return render(
		request,
		'productos/producto_list.html',
		{
			'productos': productos,
			'stock_total': stock_total,
			'total_categorias_activas': total_categorias_activas,
		},
	)


def producto_create(request):
	form = ProductoForm(request.POST or None)
	categoria_count = Categoria.objects.filter(activa=True).count()
	if request.method == 'POST' and form.is_valid():
		producto = form.save()
		notificar_stock_bajo.delay(producto.id)
		messages.success(request, 'Producto creado correctamente.')
		return redirect('productos:producto_list')
	return render(
		request,
		'productos/producto_form.html',
		{
			'form': form,
			'title': 'Crear producto',
			'submit_text': 'Guardar producto',
			'is_edit': False,
			'categoria_count': categoria_count,
		},
	)


def producto_update(request, pk):
	producto = get_object_or_404(Producto, pk=pk)
	form = ProductoForm(request.POST or None, instance=producto)
	categoria_count = Categoria.objects.filter(activa=True).count()
	if request.method == 'POST' and form.is_valid():
		producto = form.save()
		notificar_stock_bajo.delay(producto.id)
		messages.success(request, 'Producto actualizado correctamente.')
		return redirect('productos:producto_list')
	return render(
		request,
		'productos/producto_form.html',
		{
			'form': form,
			'title': 'Editar producto',
			'submit_text': 'Actualizar producto',
			'is_edit': True,
			'categoria_count': categoria_count,
		},
	)


def producto_delete(request, pk):
	producto = get_object_or_404(Producto, pk=pk)
	if request.method == 'POST':
		producto.delete()
		messages.success(request, 'Producto eliminado correctamente.')
		return redirect('productos:producto_list')
	return render(request, 'productos/producto_confirm_delete.html', {'producto': producto})


def producto_sku_sugerido(request):
	categoria_id = request.GET.get('categoria')
	if not categoria_id:
		return JsonResponse({'sku': ''})
	sku = Producto.sugerir_sku(categoria_id)
	return JsonResponse({'sku': sku})


def categoria_list(request):
	categorias = Categoria.objects.annotate(total_productos=Count('productos')).order_by('nombre')
	return render(request, 'categorias/categoria_list.html', {'categorias': categorias})


def categoria_create(request):
	form = CategoriaForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		form.save()
		messages.success(request, 'Categoria creada correctamente.')
		return redirect('productos:categoria_list')
	return render(
		request,
		'categorias/categoria_form.html',
		{
			'form': form,
			'title': 'Crear categoria',
			'submit_text': 'Guardar categoria',
		},
	)


def categoria_update(request, pk):
	categoria = get_object_or_404(Categoria, pk=pk)
	form = CategoriaForm(request.POST or None, instance=categoria)
	if request.method == 'POST' and form.is_valid():
		form.save()
		messages.success(request, 'Categoria actualizada correctamente.')
		return redirect('productos:categoria_list')
	return render(
		request,
		'categorias/categoria_form.html',
		{
			'form': form,
			'title': 'Editar categoria',
			'submit_text': 'Actualizar categoria',
		},
	)


def categoria_delete(request, pk):
	categoria = get_object_or_404(Categoria, pk=pk)
	if request.method == 'POST':
		try:
			categoria.delete()
			messages.success(request, 'Categoria eliminada correctamente.')
		except ProtectedError:
			messages.error(
				request,
				'No puedes eliminar esta categoria porque tiene productos asociados.',
			)
		return redirect('productos:categoria_list')
	return render(request, 'categorias/categoria_confirm_delete.html', {'categoria': categoria})

#Endpoints para tareas asíncronas con Celery
@csrf_exempt
@require_POST
def api_tarea_larga(request):
    task = tarea_larga_duracion.delay()
    return JsonResponse({"task_id": task.id, "status": "queued"}, status=202)


@csrf_exempt
@require_POST
def api_generar_reporte(request):
    task = generar_reporte_inventario_pdf.delay()
    status_url = reverse('productos:api_reporte_estado', args=[task.id])
    return JsonResponse({'task_id': task.id, 'status_url': status_url}, status=202)


@require_GET
def api_reporte_estado(request, task_id):
    result = AsyncResult(task_id)
    if result.successful():
        data = result.result or {}
        filename = data.get('filename')
        if filename:
            download_url = reverse('productos:reporte_descargar', args=[filename])
            return JsonResponse({'status': 'ready', 'download_url': download_url})
        return JsonResponse({'status': 'failed'}, status=500)

    if result.failed():
        return JsonResponse({'status': 'failed'}, status=500)

    return JsonResponse({'status': result.status.lower()})


@require_GET
def reporte_descargar(request, filename):
    reports_dir = Path(settings.REPORTS_DIR).resolve()
    file_path = (reports_dir / filename).resolve()
    if reports_dir not in file_path.parents or not file_path.exists():
        raise Http404('Reporte no encontrado')
    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)