from django.db import connection
from django.shortcuts import render
from core.datos_ejemplo import crear_datos_ejemplo


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


def inicio(request):
    """Página de inicio de EcoRedSV."""
    contexto = {'estado_bd': obtener_estado_bd()}
    contexto.update(crear_datos_ejemplo())
    return render(request, 'core/inicio.html', contexto)