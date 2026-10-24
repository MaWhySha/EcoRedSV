from django.contrib import admin, messages

from .models import Campania, Participacion, RegistroRecoleccion


class ParticipacionInline(admin.TabularInline):
    model = Participacion
    extra = 0


class RegistroRecoleccionInline(admin.TabularInline):
    model = RegistroRecoleccion
    extra = 0


@admin.register(Campania)
class CampaniaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_inicio', 'estado', 'organizacion', 'municipio', 'inscritos')
    list_filter = ('estado', 'municipio', 'organizacion')
    search_fields = ('titulo', 'descripcion')
    filter_horizontal = ('materiales',)
    readonly_fields = ('estado',)
    inlines = [ParticipacionInline, RegistroRecoleccionInline]
    actions = ['iniciar', 'finalizar']

    @admin.display(description='Inscritos')
    def inscritos(self, obj):
        return obj.total_inscritos()

    def _cambiar_estado(self, request, queryset, nuevo):
        for campania in queryset:
            try:
                campania.cambiar_estado(nuevo)
            except ValueError as error:
                self.message_user(request, f'{campania}: {error}', messages.ERROR)

    @admin.action(description='Iniciar las campañas seleccionadas')
    def iniciar(self, request, queryset):
        self._cambiar_estado(request, queryset, Campania.Estado.EN_CURSO)

    @admin.action(description='Finalizar las campañas seleccionadas')
    def finalizar(self, request, queryset):
        self._cambiar_estado(request, queryset, Campania.Estado.FINALIZADA)


@admin.register(Participacion)
class ParticipacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'campania', 'fecha_inscripcion', 'asistio')
    list_filter = ('asistio', 'campania')


@admin.register(RegistroRecoleccion)
class RegistroRecoleccionAdmin(admin.ModelAdmin):
    list_display = ('campania', 'material', 'peso_kg', 'registrado_por', 'fecha_registro')
    list_filter = ('campania', 'material')