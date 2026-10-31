from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from core.mixins import EliminarConProteccionMixin, PermisoRolMixin, PuedeEditarMixin
from reportes.forms import ComentarioForm, ReporteForm
from reportes.models import Comentario, ReporteAmbiental
from usuarios.models import Usuario
from usuarios.permisos import Accion


def es_administrador(usuario):
    return usuario.is_authenticated and (usuario.is_superuser or usuario.rol == Usuario.Rol.ADMIN)


def reportes_visibles(usuario):
    """El administrador ve todos; los demás, los visibles y los propios."""
    consulta = ReporteAmbiental.objects.select_related('municipio', 'autor')
    if es_administrador(usuario):
        return consulta
    if usuario.is_authenticated:
        return consulta.filter(Q(visible=True) | Q(autor=usuario))
    return consulta.filter(visible=True)


class ReporteListaView(ListView):
    """Reportes ordenados por apoyos, con filtros por estado y gravedad (RF-10, RF-20)."""

    model = ReporteAmbiental
    template_name = 'reportes/lista.html'
    context_object_name = 'reportes'
    paginate_by = 9

    def get_queryset(self):
        consulta = reportes_visibles(self.request.user).annotate(
            num_apoyos=Count('apoyos', distinct=True),
            num_comentarios=Count('comentarios', filter=Q(comentarios__visible=True), distinct=True),
        )
        estado = self.request.GET.get('estado')
        gravedad = self.request.GET.get('gravedad')
        if estado:
            consulta = consulta.filter(estado=estado)
        if gravedad:
            consulta = consulta.filter(gravedad=gravedad)
        # Los reportes con más apoyos se muestran primero (RF-20)
        return consulta.order_by('-num_apoyos', '-fecha_reporte')

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        usuario = self.request.user
        parametros = self.request.GET.copy()
        parametros.pop('page', None)
        contexto.update({
            'estados': ReporteAmbiental.Estado.choices,
            'gravedades': ReporteAmbiental.Gravedad.choices,
            'filtro_estado': self.request.GET.get('estado', ''),
            'filtro_gravedad': self.request.GET.get('gravedad', ''),
            'parametros': parametros.urlencode(),
            'puede_reportar': usuario.is_authenticated and usuario.tiene_permiso(Accion.REPORTAR),
        })
        return contexto


class ReporteDetalleView(DetailView):
    """Detalle del reporte con su historial, apoyos y comentarios (RF-11, RF-20, RF-21)."""

    model = ReporteAmbiental
    template_name = 'reportes/detalle.html'
    context_object_name = 'reporte'

    def get_queryset(self):
        return reportes_visibles(self.request.user)

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        reporte = self.object
        usuario = self.request.user
        autenticado = usuario.is_authenticated
        admin = es_administrador(usuario)
        comentarios = reporte.comentarios.select_related('usuario')
        etiquetas = dict(ReporteAmbiental.Estado.choices)
        puede_gestionar = autenticado and usuario.tiene_permiso(Accion.GESTIONAR_REPORTES)
        contexto.update({
            'seguimientos': reporte.seguimientos.select_related('responsable'),
            'comentarios': comentarios if admin else comentarios.filter(visible=True),
            'total_apoyos': reporte.total_apoyos(),
            'ya_apoyo': autenticado and reporte.apoyos.filter(usuario=usuario).exists(),
            'puede_apoyar': autenticado and usuario.tiene_permiso(Accion.APOYAR),
            'form_comentario': ComentarioForm() if autenticado and usuario.tiene_permiso(Accion.COMENTAR) else None,
            'puede_editar': autenticado and usuario.puede_editar(reporte),
            'transiciones': [(e, etiquetas[e]) for e in sorted(reporte.TRANSICIONES[reporte.estado])]
            if puede_gestionar else [],
            'es_admin': admin,
        })
        return contexto


class ReporteCrearView(PermisoRolMixin, CreateView):
    """Registro de un reporte por un usuario con correo verificado (RF-10)."""

    accion = Accion.REPORTAR
    model = ReporteAmbiental
    form_class = ReporteForm
    template_name = 'core/formulario.html'
    extra_context = {
        'titulo': 'Reportar un problema ambiental',
        'url_cancelar': reverse_lazy('reportes:lista'),
    }

    def form_valid(self, form):
        form.instance.autor = self.request.user
        messages.success(self.request, 'Su reporte se registró correctamente. Gracias por informar.')
        return super().form_valid(form)


class ReporteEditarView(PuedeEditarMixin, UpdateView):
    model = ReporteAmbiental
    form_class = ReporteForm
    template_name = 'core/formulario.html'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['titulo'] = f'Editar: {self.object}'
        contexto['url_cancelar'] = self.object.get_absolute_url()
        return contexto

    def form_valid(self, form):
        messages.success(self.request, 'Los cambios se guardaron correctamente.')
        return super().form_valid(form)


class ReporteEliminarView(PuedeEditarMixin, EliminarConProteccionMixin, DeleteView):
    model = ReporteAmbiental
    template_name = 'core/confirmar_eliminar.html'
    success_url = reverse_lazy('reportes:lista')
    mensaje_exito = 'El reporte se eliminó correctamente.'
    extra_context = {'aviso': 'También se eliminarán su historial, sus apoyos y sus comentarios.'}


@login_required
@require_POST
def apoyar(request, pk):
    """Apoya el reporte usando ReporteAmbiental.apoyar() (RF-20)."""
    reporte = get_object_or_404(ReporteAmbiental, pk=pk)
    try:
        reporte.apoyar(request.user)
        messages.success(request, 'Gracias por apoyar este reporte.')
    except (PermissionError, ValueError) as error:
        messages.error(request, str(error))
    return redirect(reporte)


@login_required
@require_POST
def comentar(request, pk):
    """Agrega un comentario usando ReporteAmbiental.comentar() (RF-21)."""
    reporte = get_object_or_404(ReporteAmbiental, pk=pk)
    try:
        reporte.comentar(request.user, request.POST.get('texto', ''))
        messages.success(request, 'Su comentario se publicó.')
    except PermissionError as error:
        messages.error(request, str(error))
    except ValidationError as error:
        messages.error(request, ' '.join(error.messages))
    return redirect(reporte)


@login_required
@require_POST
def cambiar_estado(request, pk):
    """Cambia el estado y guarda el historial usando ReporteAmbiental.cambiar_estado() (RF-11)."""
    reporte = get_object_or_404(ReporteAmbiental, pk=pk)
    try:
        reporte.cambiar_estado(
            request.POST.get('estado'),
            request.user,
            request.POST.get('comentario', '').strip(),
        )
        messages.success(request, f'El reporte ahora está: {reporte.get_estado_display()}.')
    except (PermissionError, ValueError, KeyError) as error:
        messages.error(request, str(error))
    return redirect(reporte)


@login_required
@require_POST
def ocultar_reporte(request, pk):
    """Moderación: oculta el reporte sin borrarlo (RF-22)."""
    reporte = get_object_or_404(ReporteAmbiental, pk=pk)
    try:
        reporte.ocultar(request.user)
        messages.success(request, 'El reporte quedó oculto para el público.')
    except PermissionError as error:
        messages.error(request, str(error))
    return redirect(reporte)


@login_required
@require_POST
def ocultar_comentario(request, pk, id_comentario):
    """Moderación: oculta un comentario sin borrarlo (RF-22)."""
    reporte = get_object_or_404(ReporteAmbiental, pk=pk)
    comentario = get_object_or_404(Comentario, pk=id_comentario, reporte=reporte)
    if es_administrador(request.user):
        comentario.ocultar()
        messages.success(request, 'El comentario quedó oculto.')
    else:
        messages.error(request, 'Solo el administrador puede moderar comentarios.')
    return redirect(reporte)