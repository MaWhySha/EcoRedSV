from django.urls import path

from puntos import views

app_name = 'puntos'

urlpatterns = [
    # Puntos de recepción
    path('', views.PuntoListaView.as_view(), name='lista'),
    path('nuevo/', views.PuntoCrearView.as_view(), name='crear'),
    path('<int:pk>/', views.PuntoDetalleView.as_view(), name='detalle'),
    path('<int:pk>/editar/', views.PuntoEditarView.as_view(), name='editar'),
    path('<int:pk>/eliminar/', views.PuntoEliminarView.as_view(), name='eliminar'),
    path('<int:pk>/confirmar/', views.confirmar_informacion, name='confirmar'),
    path('<int:pk>/materiales/agregar/', views.agregar_material, name='agregar_material'),
    path('<int:pk>/materiales/<int:id_material>/quitar/', views.quitar_material, name='quitar_material'),

    # Catálogo de materiales
    path('materiales/', views.MaterialListaView.as_view(), name='materiales'),
    path('materiales/nuevo/', views.MaterialCrearView.as_view(), name='crear_material'),
    path('materiales/<int:pk>/editar/', views.MaterialEditarView.as_view(), name='editar_material'),
    path('materiales/<int:pk>/eliminar/', views.MaterialEliminarView.as_view(), name='eliminar_material'),
]