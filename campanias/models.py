from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.urls import reverse

from core.models import EntidadBase, Ubicable
from usuarios.permisos import Accion


class Campania(Ubicable):
    """Campaña o jornada de recolección."""

    class Estado(models.TextChoices):
        PROGRAMADA = 'PROGRAMADA', 'Programada'
        EN_CURSO = 'EN_CURSO', 'En curso'
        FINALIZADA = 'FINALIZADA', 'Finalizada'
        CANCELADA = 'CANCELADA', 'Cancelada'

    # Cambios de estado permitidos
    TRANSICIONES = {
        'PROGRAMADA': {'EN_CURSO', 'CANCELADA'},
        'EN_CURSO': {'FINALIZADA', 'CANCELADA'},
        'FINALIZADA': set(),
        'CANCELADA': set(),
    }

    id_campania = models.AutoField(primary_key=True)
    titulo = models.CharField('título', max_length=150)
    descripcion = models.CharField('descripción', max_length=1000)
    fecha_inicio = models.DateTimeField('fecha de inicio')
    fecha_fin = models.DateTimeField('fecha de fin')
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PROGRAMADA)
    organizacion = models.ForeignKey(
        'usuarios.Organizacion',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column='id_organizacion',
        related_name='campanias',
    )
    punto = models.ForeignKey(
        'puntos.PuntoRecepcion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_punto',
        related_name='campanias',
    )
    creador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        db_column='id_creador',
        related_name='campanias_creadas',
    )
    materiales = models.ManyToManyField(
        'puntos.Material',
        related_name='campanias',
        blank=True,
        db_table='campania_material',
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campania'
        verbose_name = 'campaña'
        verbose_name_plural = 'campañas'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return self.titulo

    def get_absolute_url(self):
        return reverse('campanias:detalle', args=[self.pk])

    def clean(self):
        super().clean()
        if self.fecha_inicio and self.fecha_fin and self.fecha_fin < self.fecha_inicio:
            raise ValidationError({'fecha_fin': 'La fecha de fin no puede ser anterior al inicio.'})

    def cambiar_estado(self, nuevo):
        """Cambia el estado solo si la transición está permitida."""
        if nuevo not in self.TRANSICIONES[self.estado]:
            raise ValueError(f'No se puede pasar de {self.estado} a {nuevo}.')
        self.estado = nuevo
        self.save(update_fields=['estado', 'actualizado_en'])

    def inscribir(self, usuario):
        """Inscribe a un usuario una sola vez (RF-16)."""
        if not usuario.tiene_permiso(Accion.INSCRIBIRSE):
            raise PermissionError('El usuario no puede inscribirse (¿correo verificado?).')
        if self.estado in (self.Estado.FINALIZADA, self.Estado.CANCELADA):
            raise ValueError('La campaña ya no admite inscripciones.')
        if self.participaciones.filter(usuario=usuario).exists():
            raise ValueError('El usuario ya está inscrito.')
        return Participacion.objects.create(usuario=usuario, campania=self)

    def registrar_peso(self, material, peso_kg, usuario, observaciones=''):
        """Registra los kilogramos recolectados de un material (RF-17)."""
        if not usuario.tiene_permiso(Accion.REGISTRAR_PESO):
            raise PermissionError('El usuario no puede registrar pesos.')
        registro = RegistroRecoleccion(
            campania=self,
            material=material,
            peso_kg=Decimal(str(peso_kg)),
            registrado_por=usuario,
            observaciones=observaciones,
        )
        return registro.guardar()

    def total_recolectado(self):
        """Total de kilogramos por material (RF-18)."""
        filas = (
            self.registros.values('material__nombre')
            .annotate(total=Sum('peso_kg'))
            .order_by('material__nombre')
        )
        return {fila['material__nombre']: fila['total'] for fila in filas}

    def total_inscritos(self):
        return self.participaciones.count()

    def obtener_marcador(self):
        return {
            'tipo': 'campania',
            'titulo': self.titulo,
            'icono': 'calendario',
            'latitud': float(self.latitud),
            'longitud': float(self.longitud),
        }

    def mostrar_detalle(self):
        return (
            f'{self.titulo} · {self.municipio}. Estado: {self.get_estado_display()}. '
            f'Inscritos: {self.total_inscritos()}.'
        )


class Participacion(EntidadBase):
    """Inscripción de un usuario a una campaña (RF-16)."""

    id_participacion = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column='id_usuario',
        related_name='participaciones',
    )
    campania = models.ForeignKey(
        Campania,
        on_delete=models.CASCADE,
        db_column='id_campania',
        related_name='participaciones',
    )
    fecha_inscripcion = models.DateTimeField('fecha de inscripción', auto_now_add=True)
    asistio = models.BooleanField('asistió', default=False)

    class Meta:
        db_table = 'participacion'
        verbose_name = 'participación'
        verbose_name_plural = 'participaciones'
        constraints = [
            models.UniqueConstraint(fields=['usuario', 'campania'], name='uq_participacion_usuario_campania'),
        ]

    def __str__(self):
        return f'{self.usuario} en {self.campania}'

    def confirmar_asistencia(self):
        self.asistio = True
        self.save(update_fields=['asistio'])

    def cancelar(self):
        """Cancela la inscripción eliminándola."""
        self.delete()


class RegistroRecoleccion(EntidadBase):
    """Kilogramos recolectados de un material en una campaña (RF-17)."""

    id_registro = models.AutoField(primary_key=True)
    campania = models.ForeignKey(
        Campania,
        on_delete=models.CASCADE,
        db_column='id_campania',
        related_name='registros',
    )
    material = models.ForeignKey(
        'puntos.Material',
        on_delete=models.PROTECT,
        db_column='id_material',
        related_name='registros_recoleccion',
    )
    peso_kg = models.DecimalField(
        'peso (kg)',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        db_column='id_registrado_por',
        related_name='registros_recoleccion',
    )
    observaciones = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = 'registro_recoleccion'
        verbose_name = 'registro de recolección'
        verbose_name_plural = 'registros de recolección'
        constraints = [
            models.CheckConstraint(condition=models.Q(peso_kg__gt=0), name='ck_registro_peso_positivo'),
        ]

    def __str__(self):
        return f'{self.material}: {self.peso_kg} kg'

    def clean(self):
        """El peso solo se registra en campañas en curso o finalizadas y de materiales que reciben."""
        super().clean()
        if self.campania_id:
            if self.campania.estado not in (Campania.Estado.EN_CURSO, Campania.Estado.FINALIZADA):
                raise ValidationError('Solo se registra peso en campañas en curso o finalizadas.')
            if self.material_id and not self.campania.materiales.filter(pk=self.material_id).exists():
                raise ValidationError({'material': 'La campaña no recibe este material.'})

    def describir(self):
        return f'{self.peso_kg} kg de {self.material}, registrado por {self.registrado_por}.'