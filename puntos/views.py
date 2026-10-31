from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from core.mixins import EliminarConProteccionMixin, PermisoRolMixin, PuedeEditarMixin
from puntos.forms import AgregarMaterialForm, MaterialForm, PuntoRecepcionForm
from puntos.models import Material, PuntoRecepcion
from usuarios.models import Municipio, Usuario
from usuarios.permisos import Accion


def es_administrador(usuario):
    return usuario.is_authenticated and (usuario.is_superuser or usuario.rol == Usuario.Rol.ADMIN)


# ---------------------------------------------------------------------------
# Puntos de recepción
# ---------------------------------------------------------------------------

class PuntoListaView(ListView):
    """Consulta de puntos con búsqueda y filtros por municipio y material (RF-03, RF-05)."""

    model = PuntoRecepcion
    template_name = 'puntos/lista.html'
    context_object_name = 'puntos'
    paginate_by = 9

    def get_queryset(self):
        consulta = PuntoRecepcion.objects.select_related('municipio').prefetch_related('materiales')
        if not es_administrador(self.request.user):
            consulta = consulta.filter(activo=True)

        texto = self.request.GET.get('q', '').strip()
        municipio = self.request.GET.get('municipio')
        material = self.request.GET.get('material')
        if texto:
            consulta = consulta.filter(Q(nombre__icontains=texto) | Q(direccion__icontains=texto))
        if municipio:
            consulta = consulta.filter(municipio_id=municipio)
        if material:
            consulta = consulta.filter(materiales=material)
        return consulta.distinct()

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        usuario = self.request.user
        parametros = self.request.GET.copy()
        parametros.pop('page', None)
        contexto.update({
            'municipios': Municipio.objects.all(),
            'materiales': Material.objects.all(),
            'filtro_q': self.request.GET.get('q', ''),
            'filtro_municipio': self.request.GET.get('municipio', ''),
            'filtro_material': self.request.GET.get('material', ''),
            'parametros': parametros.urlencode(),
            'puede_registrar': usuario.is_authenticated and usuario.tiene_permiso(Accion.ACTUALIZAR_PUNTO),
        })
        return contexto


class PuntoDetalleView(DetailView):
    """Detalle de un punto: ubicación, horario, materiales y campañas (RF-04)."""

    model = PuntoRecepcion
    template_name = 'puntos/detalle.html'
    context_object_name = 'punto'

    def get_queryset(self):
        return PuntoRecepcion.objects.select_related('municipio', 'gestor')

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        punto = self.object
        usuario = self.request.user
        puede_editar = usuario.is_authenticated and usuario.puede_editar(punto)
        contexto.update({
            'detalles': punto.detalles_materiales.select_related('material'),
            'campanias': punto.campanias.all(),
            'puede_editar': puede_editar,
            'es_admin': es_administrador(usuario),
            'form_material': AgregarMaterialForm(punto=punto) if puede_editar else None,
        })
        return contexto


class PuntoCrearView(PermisoRolMixin, CreateView):
    """Registro de un punto de recepción (RF-06)."""

    accion = Accion.ACTUALIZAR_PUNTO
    model = PuntoRecepcion
    form_class = PuntoRecepcionForm
    template_name = 'core/formulario.html'
    extra_context = {
        'titulo': 'Registrar punto de recepción',
        'url_cancelar': reverse_lazy('puntos:lista'),
    }

    def form_valid(self, form):
        # Si lo registra un gestor y no eligió otro, queda como responsable
        if form.instance.gestor is None and self.request.user.rol == Usuario.Rol.GESTOR:
            form.instance.gestor = self.request.user
        messages.success(self.request, 'El punto de recepción se registró correctamente.')
        return super().form_valid(form)


class PuntoEditarView(PuedeEditarMixin, UpdateView):
    """Actualización de un punto por su gestor o un administrador (RF-07)."""

    model = PuntoRecepcion
    form_class = PuntoRecepcionForm
    template_name = 'core/formulario.html'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['titulo'] = f'Editar: {self.object}'
        contexto['url_cancelar'] = self.object.get_absolute_url()
        return contexto

    def form_valid(self, form):
        messages.success(self.request, 'Los cambios se guardaron correctamente.')
        return super().form_valid(form)


class PuntoEliminarView(PuedeEditarMixin, EliminarConProteccionMixin, DeleteView):
    """Eliminación de un punto; sus materiales asociados se borran en cascada."""

    model = PuntoRecepcion
    template_name = 'core/confirmar_eliminar.html'
    success_url = reverse_lazy('puntos:lista')
    mensaje_exito = 'El punto de recepción se eliminó correctamente.'
    extra_context = {'aviso': 'También se eliminará la lista de materiales que recibe este punto.'}


@login_required
@require_POST
def agregar_material(request, pk):
    """Agrega un material al punto usando PuntoRecepcion.agregar_material()."""
    punto = get_object_or_404(PuntoRecepcion, pk=pk)
    if not request.user.puede_editar(punto):
        messages.error(request, 'Solo el responsable del punto o un administrador pueden modificarlo.')
        return redirect(punto)

    form = AgregarMaterialForm(request.POST, punto=punto)
    if form.is_valid():
        try:
            punto.agregar_material(form.cleaned_data['material'], form.cleaned_data['observaciones'])
            messages.success(request, f'Se agregó {form.cleaned_data["material"]} al punto.')
        except ValueError as error:
            messages.error(request, str(error))
    else:
        messages.error(request, 'Seleccione un material válido.')
    return redirect(punto)


@login_required
@require_POST
def quitar_material(request, pk, id_material):
    """Quita un material del punto usando PuntoRecepcion.quitar_material()."""
    punto = get_object_or_404(PuntoRecepcion, pk=pk)
    material = get_object_or_404(Material, pk=id_material)
    if request.user.puede_editar(punto):
        punto.quitar_material(material)
        messages.success(request, f'Se quitó {material} del punto.')
    else:
        messages.error(request, 'Solo el responsable del punto o un administrador pueden modificarlo.')
    return redirect(punto)


@login_required
@require_POST
def confirmar_informacion(request, pk):
    """El administrador marca la información del punto como verificada (RF-19)."""
    punto = get_object_or_404(PuntoRecepcion, pk=pk)
    if es_administrador(request.user):
        punto.confirmar_informacion()
        messages.success(request, 'La información del punto quedó confirmada.')
    else:
        messages.error(request, 'Solo un administrador puede confirmar la información.')
    return redirect(punto)


# ---------------------------------------------------------------------------
# Catálogo de materiales (solo administradores pueden modificarlo)
# ---------------------------------------------------------------------------

class MaterialListaView(ListView):
    model = Material
    template_name = 'puntos/materiales.html'
    context_object_name = 'materiales'

    def get_queryset(self):
        return Material.objects.annotate(
            total_puntos=Count('puntos', filter=Q(puntos__activo=True), distinct=True),
        )

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['puede_gestionar'] = es_administrador(self.request.user)
        return contexto


class MaterialCrearView(PermisoRolMixin, CreateView):
    accion = Accion.MODERAR  # acción exclusiva del administrador
    model = Material
    form_class = MaterialForm
    template_name = 'core/formulario.html'
    success_url = reverse_lazy('puntos:materiales')
    extra_context = {
        'titulo': 'Registrar material',
        'url_cancelar': reverse_lazy('puntos:materiales'),
    }

    def form_valid(self, form):
        messages.success(self.request, 'El material se registró correctamente.')
        return super().form_valid(form)


class MaterialEditarView(PermisoRolMixin, UpdateView):
    accion = Accion.MODERAR
    model = Material
    form_class = MaterialForm
    template_name = 'core/formulario.html'
    success_url = reverse_lazy('puntos:materiales')

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['titulo'] = f'Editar material: {self.object}'
        contexto['url_cancelar'] = reverse_lazy('puntos:materiales')
        return contexto

    def form_valid(self, form):
        messages.success(self.request, 'Los cambios se guardaron correctamente.')
        return super().form_valid(form)


class MaterialEliminarView(PermisoRolMixin, EliminarConProteccionMixin, DeleteView):
    accion = Accion.MODERAR
    model = Material
    template_name = 'core/confirmar_eliminar.html'
    success_url = reverse_lazy('puntos:materiales')
    mensaje_exito = 'El material se eliminó correctamente.'
    extra_context = {'aviso': 'No se puede eliminar un material que ya se usa en puntos, campañas o registros.'}