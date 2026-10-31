from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from campanias.forms import CampaniaForm, RegistroPesoForm
from campanias.models import Campania
from core.mixins import EliminarConProteccionMixin, PermisoRolMixin, PuedeEditarMixin
from usuarios.permisos import Accion


class CampaniaListaView(ListView):
    """Consulta de campañas con filtro por estado (RF-09)."""

    model = Campania
    template_name = 'campanias/lista.html'
    context_object_name = 'campanias'
    paginate_by = 9

    def get_queryset(self):
        consulta = Campania.objects.select_related('municipio', 'organizacion').annotate(
            inscritos=Count('participaciones', distinct=True),
        )
        estado = self.request.GET.get('estado')
        if estado:
            consulta = consulta.filter(estado=estado)
        return consulta

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        usuario = self.request.user
        parametros = self.request.GET.copy()
        parametros.pop('page', None)
        contexto.update({
            'estados': Campania.Estado.choices,
            'filtro_estado': self.request.GET.get('estado', ''),
            'parametros': parametros.urlencode(),
            'puede_registrar': usuario.is_authenticated and usuario.tiene_permiso(Accion.REGISTRAR_CAMPANIA),
        })
        return contexto


class CampaniaDetalleView(DetailView):
    """Detalle de una campaña: materiales, inscripciones y resultados (RF-09, RF-18)."""

    model = Campania
    template_name = 'campanias/detalle.html'
    context_object_name = 'campania'

    def get_queryset(self):
        return Campania.objects.select_related('municipio', 'organizacion', 'punto', 'creador')

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        campania = self.object
        usuario = self.request.user
        puede_editar = usuario.is_authenticated and usuario.puede_editar(campania)
        totales = campania.total_recolectado()
        puede_registrar_peso = (
            puede_editar
            and usuario.tiene_permiso(Accion.REGISTRAR_PESO)
            and campania.estado in (Campania.Estado.EN_CURSO, Campania.Estado.FINALIZADA)
        )
        etiquetas = dict(Campania.Estado.choices)
        contexto.update({
            'materiales': campania.materiales.all(),
            'totales': totales,
            'total_kg': sum(totales.values()),
            'registros': campania.registros.select_related('material', 'registrado_por'),
            'participaciones': campania.participaciones.select_related('usuario'),
            'inscrito': usuario.is_authenticated and campania.participaciones.filter(usuario=usuario).exists(),
            'abierta': campania.estado in (Campania.Estado.PROGRAMADA, Campania.Estado.EN_CURSO),
            'puede_editar': puede_editar,
            'transiciones': [(e, etiquetas[e]) for e in sorted(campania.TRANSICIONES[campania.estado])]
            if puede_editar else [],
            'form_peso': RegistroPesoForm(campania=campania) if puede_registrar_peso else None,
        })
        return contexto


class CampaniaCrearView(PermisoRolMixin, CreateView):
    """Registro de una campaña por una organización o un administrador (RF-08)."""

    accion = Accion.REGISTRAR_CAMPANIA
    model = Campania
    form_class = CampaniaForm
    template_name = 'core/formulario.html'
    extra_context = {
        'titulo': 'Registrar campaña',
        'url_cancelar': reverse_lazy('campanias:lista'),
    }

    def form_valid(self, form):
        form.instance.creador = self.request.user
        # Si la registra el encargado de una organización, se asocia a ella
        if form.instance.organizacion is None and self.request.user.organizacion_id:
            form.instance.organizacion = self.request.user.organizacion
        messages.success(self.request, 'La campaña se registró correctamente.')
        return super().form_valid(form)


class CampaniaEditarView(PuedeEditarMixin, UpdateView):
    model = Campania
    form_class = CampaniaForm
    template_name = 'core/formulario.html'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['titulo'] = f'Editar: {self.object}'
        contexto['url_cancelar'] = self.object.get_absolute_url()
        return contexto

    def form_valid(self, form):
        messages.success(self.request, 'Los cambios se guardaron correctamente.')
        return super().form_valid(form)


class CampaniaEliminarView(PuedeEditarMixin, EliminarConProteccionMixin, DeleteView):
    model = Campania
    template_name = 'core/confirmar_eliminar.html'
    success_url = reverse_lazy('campanias:lista')
    mensaje_exito = 'La campaña se eliminó correctamente.'
    extra_context = {'aviso': 'También se eliminarán sus inscripciones, materiales y registros de peso.'}


@login_required
@require_POST
def inscribirse(request, pk):
    """Inscribe al usuario usando Campania.inscribir() (RF-16)."""
    campania = get_object_or_404(Campania, pk=pk)
    try:
        campania.inscribir(request.user)
        messages.success(request, 'Su inscripción a la campaña quedó registrada.')
    except (PermissionError, ValueError) as error:
        messages.error(request, str(error))
    return redirect(campania)


@login_required
@require_POST
def cancelar_inscripcion(request, pk):
    """Cancela la inscripción del usuario usando Participacion.cancelar()."""
    campania = get_object_or_404(Campania, pk=pk)
    if campania.estado in (Campania.Estado.FINALIZADA, Campania.Estado.CANCELADA):
        messages.error(request, 'No se puede cancelar la inscripción de una campaña que ya terminó.')
        return redirect(campania)
    participacion = campania.participaciones.filter(usuario=request.user).first()
    if participacion:
        participacion.cancelar()
        messages.success(request, 'Su inscripción fue cancelada.')
    return redirect(campania)


@login_required
@require_POST
def cambiar_estado(request, pk):
    """Cambia el estado usando Campania.cambiar_estado(), que valida la transición."""
    campania = get_object_or_404(Campania, pk=pk)
    if not request.user.puede_editar(campania):
        messages.error(request, 'Solo el responsable de la campaña o un administrador pueden cambiar su estado.')
        return redirect(campania)
    try:
        campania.cambiar_estado(request.POST.get('estado'))
        messages.success(request, f'La campaña ahora está: {campania.get_estado_display()}.')
    except (ValueError, KeyError) as error:
        messages.error(request, str(error))
    return redirect(campania)


@login_required
@require_POST
def registrar_peso(request, pk):
    """Registra kilogramos usando Campania.registrar_peso() (RF-17)."""
    campania = get_object_or_404(Campania, pk=pk)
    if not request.user.puede_editar(campania):
        messages.error(request, 'Solo el responsable de la campaña o un administrador pueden registrar pesos.')
        return redirect(campania)

    form = RegistroPesoForm(request.POST, campania=campania)
    if not form.is_valid():
        messages.error(request, 'Revise el material y el peso: el peso debe ser mayor que cero.')
        return redirect(campania)
    try:
        registro = campania.registrar_peso(
            form.cleaned_data['material'],
            form.cleaned_data['peso_kg'],
            request.user,
            form.cleaned_data['observaciones'],
        )
        messages.success(request, f'Se registraron {registro.peso_kg} kg de {registro.material}.')
    except PermissionError as error:
        messages.error(request, str(error))
    except ValidationError as error:
        messages.error(request, ' '.join(error.messages))
    return redirect(campania)