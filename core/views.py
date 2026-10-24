from django.db import connection
from django.shortcuts import render

from campanias.models import Campania
from puntos.models import Material, PuntoRecepcion
from reportes.models import ReporteAmbiental
from usuarios.models import Municipio, Organizacion, Usuario


def obtener_estado_bd():
    """Comprueba la conexión con SQL Server y devuelve un resumen."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT DB_NAME(), @@VERSION")
            nombre, version = cursor.fetchone()
        return {
            'conectado': True,
            'base': nombre,
            'version': version.splitlines()[0],
        }
    except Exception as error:
        return {'conectado': False, 'error': str(error)}


def contar_registros():
    """Cantidad de registros guardados en las tablas principales."""
    modelos = [Usuario, Municipio, Organizacion, Material, PuntoRecepcion, Campania, ReporteAmbiental]
    return [(m._meta.verbose_name_plural.capitalize(), m.objects.count()) for m in modelos]


def construir_marcadores():
    """
    Genera los marcadores del mapa sin importar el tipo de cada elemento.
    Cada modelo responde a obtener_marcador() a su manera (polimorfismo).
    """
    elementos = [
        *PuntoRecepcion.objects.filter(activo=True),
        *Campania.objects.all(),
        *ReporteAmbiental.objects.filter(visible=True),
    ]
    return [elemento.obtener_marcador() for elemento in elementos]


def inicio(request):
    """Página de inicio de EcoRedSV."""
    contexto = {'estado_bd': obtener_estado_bd()}
    if contexto['estado_bd']['conectado']:
        contexto['conteos'] = contar_registros()
        contexto['marcadores'] = construir_marcadores()
    return render(request, 'core/inicio.html', contexto)