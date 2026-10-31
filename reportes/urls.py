from django.urls import path

from reportes import views

app_name = 'reportes'

urlpatterns = [
    path('', views.ReporteListaView.as_view(), name='lista'),
    path('nuevo/', views.ReporteCrearView.as_view(), name='crear'),
    path('<int:pk>/', views.ReporteDetalleView.as_view(), name='detalle'),
    path('<int:pk>/editar/', views.ReporteEditarView.as_view(), name='editar'),
    path('<int:pk>/eliminar/', views.ReporteEliminarView.as_view(), name='eliminar'),
    path('<int:pk>/apoyar/', views.apoyar, name='apoyar'),
    path('<int:pk>/comentar/', views.comentar, name='comentar'),
    path('<int:pk>/estado/', views.cambiar_estado, name='cambiar_estado'),
    path('<int:pk>/ocultar/', views.ocultar_reporte, name='ocultar'),
    path('<int:pk>/comentarios/<int:id_comentario>/ocultar/', views.ocultar_comentario, name='ocultar_comentario'),
]