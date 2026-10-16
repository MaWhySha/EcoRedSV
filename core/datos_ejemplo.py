from datetime import timedelta

from django.utils import timezone

from campanias.dominio import Campania
from core.base import construir_marcadores
from puntos.dominio import Material, PuntoRecepcion
from reportes.dominio import ReporteAmbiental, ordenar_por_apoyos
from usuarios.permisos import Accion, PerfilUsuario, Rol


def crear_datos_ejemplo():
    """
    Crea objetos de ejemplo para comprobar las clases.
    Son datos ficticios en memoria: no se guardan en la base de datos.
    """
    # Usuarios con distintos roles
    vecina = PerfilUsuario('ana', Rol.COMUNIDAD, correo_verificado=True)
    gestor = PerfilUsuario('gestor_punto', Rol.GESTOR, correo_verificado=True)
    organizacion = PerfilUsuario('org_ejemplo', Rol.ORGANIZACION, correo_verificado=True)
    admin = PerfilUsuario('admin', Rol.ADMIN, correo_verificado=True)
    sin_verificar = PerfilUsuario('usuario_nuevo', Rol.COMUNIDAD)

    # Materiales
    pet = Material('Botellas PET', 'Plástico', 'Limpias y sin tapón')
    latas = Material('Latas de aluminio', 'Metal', 'Aplastadas')
    carton = Material('Cartón', 'Papel y cartón', 'Seco y doblado')

    # Punto de recepción
    punto = PuntoRecepcion(
        'Punto de ejemplo', 'Centro de acopio', 'Barrio El Centro',
        14.040, -88.938, 'Chalatenango',
        horario='Lunes a viernes, 8:00 a 16:00', gestor='gestor_punto',
    )
    punto.agregar_material(pet, 'Solo botellas sin tapón')
    punto.agregar_material(latas)
    punto.confirmar_informacion()

    # Campaña con inscripción y pesos registrados
    inicio = timezone.now()
    campania = Campania(
        'Jornada de reciclaje de ejemplo', inicio, inicio + timedelta(hours=4),
        'Colonia Veracruz', 14.032, -88.942, 'Chalatenango',
        creador='org_ejemplo', punto=punto,
    )
    campania.materiales = [pet, latas, carton]
    campania.inscribir(vecina)
    campania.cambiar_estado(Campania.EN_CURSO)
    campania.registrar_peso(pet, 12.5, organizacion)
    campania.registrar_peso(latas, 4.2, organizacion)
    campania.registrar_peso(pet, 3.5, organizacion)

    # Reportes con apoyos y cambio de estado
    reporte_alto = ReporteAmbiental(
        'Basura acumulada en la esquina', 'Bolsas de basura junto a la cuneta.',
        'ALTA', 'Colonia Veracruz', 14.035, -88.945, 'Chalatenango', autor='ana',
    )
    reporte_alto.apoyar(vecina)
    reporte_alto.apoyar(gestor)
    reporte_alto.cambiar_estado(ReporteAmbiental.EN_REVISION, admin, 'Se notificó a la alcaldía.')

    reporte_medio = ReporteAmbiental(
        'Depósito de basura lleno', 'El depósito del parque no se ha vaciado.',
        'MEDIA', 'Parque central', 14.038, -88.940, 'Chalatenango', autor='ana',
    )
    reporte_medio.apoyar(organizacion)

    # Todos los elementos pasan su validación antes de "guardarse"
    elementos = [punto, campania, reporte_alto, reporte_medio]
    for elemento in elementos:
        elemento.guardar()

    # Ejemplo de validación: un peso negativo se rechaza
    try:
        campania.registrar_peso(carton, -2, organizacion)
        error_validacion = None
    except ValueError as error:
        error_validacion = str(error)

    pruebas_permisos = [
        ('ana (COMUNIDAD) puede reportar', vecina.tiene_permiso(Accion.REPORTAR)),
        ('usuario_nuevo sin correo verificado puede reportar', sin_verificar.tiene_permiso(Accion.REPORTAR)),
        ('ana (COMUNIDAD) puede registrar campañas', vecina.tiene_permiso(Accion.REGISTRAR_CAMPANIA)),
        ('gestor_punto puede editar su punto', gestor.puede_editar(punto)),
        ('ana puede editar el punto', vecina.puede_editar(punto)),
    ]

    return {
        'elementos': elementos,
        'marcadores': construir_marcadores(elementos),
        'resultados': campania.total_recolectado(),
        'reportes': ordenar_por_apoyos([reporte_medio, reporte_alto]),
        'historial': reporte_alto.historial,
        'permisos': pruebas_permisos,
        'error_validacion': error_validacion,
    }