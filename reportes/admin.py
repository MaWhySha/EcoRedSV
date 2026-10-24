from django.contrib import admin, messages

from .models import Apoyo, Comentario, ReporteAmbiental, SeguimientoReporte


class SeguimientoInline(admin.TabularInline):
    """Historial de estados: solo lectura, se crea automáticamente."""
    model = SeguimientoReporte
    extra = 0
    can_delete = False
    readonly_fields = ('estado_anterior', 'estado_nuevo', 'responsable', 'comentario', 'fecha')

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ReporteAmbiental)
class ReporteAmbientalAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'gravedad', 'estado', 'municipio', 'autor', 'apoyos', 'visible')
    list_filter = ('estado', 'gravedad', 'municipio', 'visible')
    search_fields = ('titulo', 'descripcion')
    readonly_fields = ('estado',)
    inlines = [SeguimientoInline]
    actions = ['poner_en_revision', 'marcar_atendido', 'descartar', 'ocultar']

    @admin.display(description='Apoyos')
    def apoyos(self, obj):
        return obj.total_apoyos()

    def _cambiar_estado(self, request, queryset, nuevo):
        for reporte in queryset:
            try:
                reporte.cambiar_estado(nuevo, request.user, 'Cambio desde el panel de administración.')
            except (ValueError, PermissionError) as error:
                self.message_user(request, f'{reporte}: {error}', messages.ERROR)

    @admin.action(description='Poner en revisión')
    def poner_en_revision(self, request, queryset):
        self._cambiar_estado(request, queryset, ReporteAmbiental.Estado.EN_REVISION)

    @admin.action(description='Marcar como atendido')
    def marcar_atendido(self, request, queryset):
        self._cambiar_estado(request, queryset, ReporteAmbiental.Estado.ATENDIDO)

    @admin.action(description='Descartar')
    def descartar(self, request, queryset):
        self._cambiar_estado(request, queryset, ReporteAmbiental.Estado.DESCARTADO)

    @admin.action(description='Ocultar (moderación)')
    def ocultar(self, request, queryset):
        for reporte in queryset:
            reporte.ocultar(request.user)


@admin.register(SeguimientoReporte)
class SeguimientoReporteAdmin(admin.ModelAdmin):
    list_display = ('reporte', 'estado_anterior', 'estado_nuevo', 'responsable', 'fecha')
    list_filter = ('estado_nuevo',)


@admin.register(Apoyo)
class ApoyoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'reporte', 'campania', 'fecha')


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'texto', 'reporte', 'campania', 'visible', 'fecha')
    list_filter = ('visible',)
    actions = ['ocultar']

    @admin.action(description='Ocultar (moderación)')
    def ocultar(self, request, queryset):
        for comentario in queryset:
            comentario.ocultar()