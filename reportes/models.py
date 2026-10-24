from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models, transaction
from django.db.models import Q

from core.models import EntidadBase, Ubicable
from usuarios.permisos import Accion


def validar_tamano_imagen(archivo):
    """Las fotografías no pueden superar los 5 MB (RNF-09)."""
    if archivo.size > 5 * 1024 * 1024:
        raise ValidationError('La fotografía no puede superar los 5 MB.')


class ReporteAmbiental(Ubicable):
    """Problema ambiental reportado por un usuario."""

    class Gravedad(models.TextChoices):
        BAJA = 'BAJA', 'Baja'
        MEDIA = 'MEDIA', 'Media'
        ALTA = 'ALTA', 'Alta'

    class Estado(models.TextChoices):
        RECIBIDO = 'RECIBIDO', 'Recibido'
        EN_REVISION = 'EN_REVISION', 'En revisión'
        ATENDIDO = 'ATENDIDO', 'Atendido'
        DESCARTADO = 'DESCARTADO', 'Descartado'

    TRANSICIONES = {
        'RECIBIDO': {'EN_REVISION', 'DESCARTADO'},
        'EN_REVISION': {'ATENDIDO', 'DESCARTADO'},
        'ATENDIDO': set(),
        'DESCARTADO': set(),
    }

    id_reporte = models.AutoField(primary_key=True)
    titulo = models.CharField('título', max_length=100)
    descripcion = models.CharField('descripción', max_length=500)
    direccion = models.CharField('dirección', max_length=250, blank=True)  # opcional en reportes
    gravedad = models.CharField(max_length=10, choices=Gravedad.choices)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.RECIBIDO)
    visible = models.BooleanField(default=True)
    fotografia = models.FileField(
        'fotografía',
        upload_to='reportes/',
        max_length=255,
        blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png']), validar_tamano_imagen],
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        db_column='id_autor',
        related_name='reportes',
    )
    fecha_reporte = models.DateTimeField('fecha del reporte', auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reporte_ambiental'
        verbose_name = 'reporte ambiental'
        verbose_name_plural = 'reportes ambientales'
        ordering = ['-fecha_reporte']

    def __str__(self):
        return self.titulo

    @transaction.atomic
    def cambiar_estado(self, nuevo, usuario, comentario=''):
        """Valida el cambio y deja constancia en el historial (RF-11)."""
        if not usuario.tiene_permiso(Accion.GESTIONAR_REPORTES):
            raise PermissionError('El usuario no puede gestionar reportes.')
        if nuevo not in self.TRANSICIONES[self.estado]:
            raise ValueError(f'No se puede pasar de {self.estado} a {nuevo}.')
        anterior = self.estado
        self.estado = nuevo
        self.save(update_fields=['estado', 'actualizado_en'])
        return SeguimientoReporte.objects.create(
            reporte=self,
            responsable=usuario,
            estado_anterior=anterior,
            estado_nuevo=nuevo,
            comentario=comentario,
        )

    def apoyar(self, usuario):
        """Un usuario apoya el reporte una sola vez (RF-20)."""
        if not usuario.tiene_permiso(Accion.APOYAR):
            raise PermissionError('El usuario no puede apoyar (¿correo verificado?).')
        if self.apoyos.filter(usuario=usuario).exists():
            raise ValueError('El usuario ya apoyó este reporte.')
        return Apoyo.objects.create(usuario=usuario, reporte=self)

    def comentar(self, usuario, texto):
        """Agrega un comentario validado (RF-21)."""
        if not usuario.tiene_permiso(Accion.COMENTAR):
            raise PermissionError('El usuario no puede comentar (¿correo verificado?).')
        return Comentario(usuario=usuario, reporte=self, texto=texto).guardar()

    def ocultar(self, usuario):
        """Moderación: oculta el reporte sin borrarlo (RF-22)."""
        if not usuario.tiene_permiso(Accion.MODERAR):
            raise PermissionError('Solo el administrador puede moderar.')
        self.visible = False
        self.save(update_fields=['visible', 'actualizado_en'])

    def total_apoyos(self):
        return self.apoyos.count()

    def obtener_marcador(self):
        return {
            'tipo': 'reporte',
            'titulo': self.titulo,
            'icono': f'alerta-{self.gravedad.lower()}',
            'latitud': float(self.latitud),
            'longitud': float(self.longitud),
        }

    def mostrar_detalle(self):
        return (
            f'{self.titulo} · {self.municipio}. Gravedad: {self.get_gravedad_display()}. '
            f'Estado: {self.get_estado_display()}. Apoyos: {self.total_apoyos()}.'
        )


class SeguimientoReporte(EntidadBase):
    """Historial de cambios de estado de un reporte."""

    id_seguimiento = models.AutoField(primary_key=True)
    reporte = models.ForeignKey(
        ReporteAmbiental,
        on_delete=models.CASCADE,
        db_column='id_reporte',
        related_name='seguimientos',
    )
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        db_column='id_responsable',
        related_name='seguimientos_reportes',
    )
    estado_anterior = models.CharField(max_length=20, choices=ReporteAmbiental.Estado.choices)
    estado_nuevo = models.CharField(max_length=20, choices=ReporteAmbiental.Estado.choices)
    comentario = models.CharField(max_length=500, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'seguimiento_reporte'
        verbose_name = 'seguimiento de reporte'
        verbose_name_plural = 'seguimientos de reportes'
        ordering = ['fecha']

    def __str__(self):
        return f'{self.reporte}: {self.estado_anterior} → {self.estado_nuevo}'

    def describir(self):
        return (
            f'{self.get_estado_anterior_display()} → {self.get_estado_nuevo_display()} '
            f'por {self.responsable}'
        )


# Cada apoyo o comentario pertenece a un reporte o a una campaña, nunca a ambos ni a ninguno
UN_SOLO_ELEMENTO = (
    Q(reporte__isnull=False, campania__isnull=True)
    | Q(reporte__isnull=True, campania__isnull=False)
)


class Apoyo(EntidadBase):
    """Respaldo de un usuario a un reporte o a una campaña (RF-20)."""

    id_apoyo = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column='id_usuario',
        related_name='apoyos',
    )
    reporte = models.ForeignKey(
        ReporteAmbiental,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='id_reporte',
        related_name='apoyos',
    )
    campania = models.ForeignKey(
        'campanias.Campania',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='id_campania',
        related_name='apoyos',
    )
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'apoyo'
        constraints = [
            models.CheckConstraint(condition=UN_SOLO_ELEMENTO, name='ck_apoyo_un_elemento'),
            models.UniqueConstraint(
                fields=['usuario', 'reporte'],
                condition=Q(reporte__isnull=False),
                name='uq_apoyo_usuario_reporte',
            ),
            models.UniqueConstraint(
                fields=['usuario', 'campania'],
                condition=Q(campania__isnull=False),
                name='uq_apoyo_usuario_campania',
            ),
        ]

    def __str__(self):
        return f'{self.usuario} apoya: {self.elemento_apoyado()}'

    def clean(self):
        super().clean()
        if bool(self.reporte_id) == bool(self.campania_id):
            raise ValidationError('El apoyo debe pertenecer a un reporte o a una campaña, no a ambos.')

    def elemento_apoyado(self):
        """Devuelve el reporte o la campaña apoyada."""
        return self.reporte or self.campania


class Comentario(EntidadBase):
    """Comentario de un usuario sobre un reporte o una campaña (RF-21)."""

    id_comentario = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column='id_usuario',
        related_name='comentarios',
    )
    reporte = models.ForeignKey(
        ReporteAmbiental,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='id_reporte',
        related_name='comentarios',
    )
    campania = models.ForeignKey(
        'campanias.Campania',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_column='id_campania',
        related_name='comentarios',
    )
    texto = models.CharField(max_length=500)
    visible = models.BooleanField(default=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comentario'
        ordering = ['fecha']
        constraints = [
            models.CheckConstraint(condition=UN_SOLO_ELEMENTO, name='ck_comentario_un_elemento'),
        ]

    def __str__(self):
        return f'Comentario de {self.usuario}'

    def clean(self):
        super().clean()
        if bool(self.reporte_id) == bool(self.campania_id):
            raise ValidationError('El comentario debe pertenecer a un reporte o a una campaña, no a ambos.')
        if not self.texto.strip():
            raise ValidationError({'texto': 'El comentario no puede estar vacío.'})

    def ocultar(self):
        """Moderación: oculta el comentario sin borrarlo (RF-22)."""
        self.visible = False
        self.save(update_fields=['visible'])