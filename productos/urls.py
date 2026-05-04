from django.urls import path

from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.producto_list, name='producto_list'),
    path('productos/nuevo/', views.producto_create, name='producto_create'),
    path('productos/sku-sugerido/', views.producto_sku_sugerido, name='producto_sku_sugerido'),
    path('productos/<int:pk>/editar/', views.producto_update, name='producto_update'),
    path('productos/<int:pk>/eliminar/', views.producto_delete, name='producto_delete'),
    path('categorias/', views.categoria_list, name='categoria_list'),
    path('categorias/nueva/', views.categoria_create, name='categoria_create'),
    path('categorias/<int:pk>/editar/', views.categoria_update, name='categoria_update'),
    path('categorias/<int:pk>/eliminar/', views.categoria_delete, name='categoria_delete'),
    path("api/tarea-larga/", views.api_tarea_larga, name="api_tarea_larga"),
]
