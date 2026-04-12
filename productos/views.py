from django.contrib import messages
from django.db.models import Count, ProtectedError, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

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
		form.save()
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
		form.save()
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
