from enum import Enum


class Rol(Enum):
    """Roles del sistema definidos en la Semana 3."""
    COMUNIDAD = 'COMUNIDAD'
    GESTOR = 'GESTOR'
    ORGANIZACION = 'ORGANIZACION'
    ADMIN = 'ADMIN'


class Accion(Enum):
    """Acciones que requieren permiso."""
    REPORTAR = 'reportar'
    APOYAR = 'apoyar'
    COMENTAR = 'comentar'
    INSCRIBIRSE = 'inscribirse'
    ACTUALIZAR_PUNTO = 'actualizar_punto'
    REGISTRAR_CAMPANIA = 'registrar_campania'
    REGISTRAR_PESO = 'registrar_peso'
    GESTIONAR_REPORTES = 'gestionar_reportes'
    MODERAR = 'moderar'
    PUBLICAR_CONTENIDO = 'publicar_contenido'


# Cada rol tiene los permisos del anterior más los suyos (sección 3.4)
_PERMISOS_COMUNIDAD = {
    Accion.REPORTAR, Accion.APOYAR, Accion.COMENTAR, Accion.INSCRIBIRSE,
}
_PERMISOS_GESTOR = _PERMISOS_COMUNIDAD | {Accion.ACTUALIZAR_PUNTO}
_PERMISOS_ORGANIZACION = _PERMISOS_GESTOR | {
    Accion.REGISTRAR_CAMPANIA, Accion.REGISTRAR_PESO,
}

PERMISOS_POR_ROL = {
    Rol.COMUNIDAD: _PERMISOS_COMUNIDAD,
    Rol.GESTOR: _PERMISOS_GESTOR,
    Rol.ORGANIZACION: _PERMISOS_ORGANIZACION,
    Rol.ADMIN: set(Accion),
}

# Acciones que exigen correo verificado (RF-01)
REQUIEREN_CORREO_VERIFICADO = {
    Accion.REPORTAR, Accion.APOYAR, Accion.COMENTAR, Accion.INSCRIBIRSE,
}