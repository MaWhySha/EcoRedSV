from django.urls import path

from campanias import views

app_name = 'campanias'

urlpatterns = [
    path('', views.CampaniaListaView.as_view(), name='lista'),
    path('nueva/', views.CampaniaCrearView.as_view(), name='crear'),
    path('<int:pk>/', views.CampaniaDetalleView.as_view(), name='detalle'),
    path('<int:pk>/editar/', views.CampaniaEditarView.as_view(), name='editar'),
    path('<int:pk>/eliminar/', views.CampaniaEliminarView.as_view(), name='eliminar'),
    path('<int:pk>/inscribirse/', views.inscribirse, name='inscribirse'),
    path('<int:pk>/cancelar-inscripcion/', views.cancelar_inscripcion, name='cancelar_inscripcion'),
    path('<int:pk>/estado/', views.cambiar_estado, name='cambiar_estado'),
    path('<int:pk>/peso/', views.registrar_peso, name='registrar_peso'),
]