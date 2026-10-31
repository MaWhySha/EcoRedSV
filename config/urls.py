from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cuentas/', include('django.contrib.auth.urls')),
    path('puntos/', include('puntos.urls')),
    path('campanias/', include('campanias.urls')),
    path('', include('core.urls')),
]

# En desarrollo, Django sirve las fotografías subidas
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)