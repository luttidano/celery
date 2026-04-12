from django.contrib import admin

from .models import Categoria, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
	list_display = ('id', 'nombre', 'prefijo_sku', 'activa')
	list_filter = ('activa',)
	search_fields = ('nombre', 'prefijo_sku')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
	list_display = ('id', 'sku', 'nombre', 'categoria', 'cantidad', 'precio')
	list_filter = ('categoria',)
	search_fields = ('sku', 'nombre', 'categoria__nombre')
