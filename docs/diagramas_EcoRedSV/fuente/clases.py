from engine import *
import engine
D=Diagram(990,668)
# texto azul para atributos de referencia: marcamos con prefijo '@'
_orig=engine.cbox
def cb(name,x,y,w,attrs,meths,**k):
    b=_orig(D,name,x,y,w,[a.lstrip('@') for a in attrs],meths,**k)
    # recolorear atributos con @
    lh=11.2; hh=HH+(9 if k.get('stereo') else 0); yy=y+hh+3
    for a in attrs:
        if a.startswith('@'):
            D.ax.add_patch(Rectangle((x+1,yy+0.5),w-2,lh-1,fc='#E6F0FA',ec='none',zorder=3.5))
            for t in D.ax.texts[::-1]:
                if t.get_text()==a.lstrip('@') and abs(t.get_position()[1]-(yy+lh/2))<0.1:
                    t.set_color(BLUE); t.set_fontweight('bold'); break
        yy+=lh
    return b
D.area(5,5,345,212,'Usuarios','#EEF3F9')
D.area(360,5,625,212,'Clases base','#F3F3F3')
D.area(5,236,300,395,'Puntos y materiales','#EEF6F1')
D.area(315,236,272,395,'Campañas','#FBF4EA')
D.area(597,236,388,395,'Reportes y participación','#F4F0F8')
cb('Municipio',15,28,130,['- nombre: str','- departamento: str'],['+ listar_puntos()'])
cb('Organizacion',15,104,130,['- nombre: str','- tipo: str','- correo_contacto: str','- telefono_contacto: str'],['+ listar_campanias()'])
cb('Usuario',175,28,165,['- nombre_usuario: str','- correo: str','- correo_verificado: bool','- _contrasena: str (hash)','- rol: Rol','- municipio: Municipio','- organizacion: Organizacion'],
   ['+ registrar()','+ verificar_correo()','+ iniciar_sesion()','+ tiene_permiso(accion): bool','+ puede_editar(objeto): bool'])
cb('EntidadBase',455,28,160,['- _creado_en: DateTime','- _actualizado_en: DateTime'],['+ guardar()','+ validar()*'],stereo=True)
cb('Ubicable',700,28,180,['- direccion: str','- latitud: Decimal','- longitud: Decimal','@- municipio: Municipio'],['+ obtener_marcador(): dict*','+ mostrar_detalle()*'],stereo=True)
RY=250
cb('PuntoRecepcion',12,RY,160,['- nombre: str','- tipo: TipoPunto','- horario: str','- condiciones_entrega: str','- estado_informacion: str','@- gestor: Usuario'],
   ['+ agregar_material()','+ quitar_material()','+ confirmar_informacion()','+ obtener_marcador()','+ mostrar_detalle()'])
cb('Material',182,RY,118,['- nombre: str','- categoria: str','- descripcion: str','- indicaciones: str'],['+ puntos_que_lo_reciben()','+ mostrar_detalle()'])
cb('Campania',355,RY,185,['- titulo: str','- descripcion: str','- fecha_inicio: DateTime','- fecha_fin: DateTime','- estado: str','@- organizacion: Organizacion','- punto: PuntoRecepcion','@- creador: Usuario','- materiales: Material[]'],
   ['+ publicar()','+ inscribir(usuario)','+ cambiar_estado()','+ total_recolectado(): Decimal','+ apoyar(usuario)','+ comentar(usuario, texto)','+ obtener_marcador()'])
cb('ReporteAmbiental',697.5,RY,185,['- titulo: str','- descripcion: str','- gravedad: str','- _estado: str','- visible: bool','- fotografia: Imagen','@- autor: Usuario'],
   ['+ registrar()','+ cambiar_estado(nuevo, usuario)','+ apoyar(usuario)','+ comentar(usuario, texto)','+ ocultar()','+ obtener_marcador()','+ mostrar_detalle()'])
R3=495
cb('PuntoMaterial',12,R3,135,['- punto: PuntoRecepcion','- material: Material','- observaciones: str'],[],assoc=True)
cb('ContenidoEducativo',157,R3,140,['- titulo: str','- contenido: str','- material: Material','@- autor: Usuario','- publicado: bool'],['+ publicar()','+ mostrar_detalle()'])
cb('RegistroRecoleccion',322,R3,125,['- campania: Campania','- material: Material','- _peso_kg: Decimal','@- registrado_por: Usuario'],['+ registrar()','+ validar()'])
cb('Participacion',455,R3,125,['@- usuario: Usuario','- campania: Campania','- fecha_inscripcion: DateTime','- asistio: bool'],['+ confirmar_asistencia()','+ cancelar()'],assoc=True)
cb('Apoyo',604,R3,118,['@- usuario: Usuario','- reporte: ReporteAmbiental','- campania: Campania','- fecha: DateTime'],['+ validar()'],assoc=True)
cb('Comentario',732,R3,124,['@- usuario: Usuario','- reporte: ReporteAmbiental','- campania: Campania','- texto: str','- visible: bool'],['+ ocultar()','+ validar()'])
cb('SeguimientoReporte',864,R3,116,['- estado_anterior: str','- estado_nuevo: str','- comentario: str','@- responsable: Usuario'],[])
b=D.boxes; L=D.link
def P(n,side,t=None,x=None,y=None):
    B=b[n]
    if side in 'tb':
        xv=x if x is not None else B['x']+(t if t is not None else .5)*B['w']
        return (xv, B['y'] if side=='t' else B['y']+B['h'], side)
    yv=y if y is not None else B['y']+(t if t is not None else .5)*B['h']
    return (B['x'] if side=='l' else B['x']+B['w'], yv, side)
# Usuarios
L(P('Municipio','r',y=60),P('Usuario','l',y=60),BLUE)
L(P('Organizacion','r',y=150),P('Usuario','l',y=150),BLUE)
# herencia
D.inherit(P('Ubicable','l',y=70),P('EntidadBase','r',y=70),via='direct') if False else None
D.ax.plot([700,615],[70,70],color=GREY,lw=1.3,zorder=2); D._sym((615,70),(700,70),'tri',GREY)
BUS=226
ubx=b['Ubicable']['x']+b['Ubicable']['w']/2; uby=b['Ubicable']['y']+b['Ubicable']['h']
for n in ['PuntoRecepcion','Campania','ReporteAmbiental']:
    cx=b[n]['x']+b[n]['w']/2
    D.ax.plot([cx,cx],[RY,BUS],color=GREY,lw=1.3,zorder=2)
D.ax.plot([b['PuntoRecepcion']['x']+80,ubx],[BUS,BUS],color=GREY,lw=1.3,zorder=2)
D.ax.plot([ubx,ubx],[BUS,uby],color=GREY,lw=1.3,zorder=2)
D._sym((ubx,uby),(ubx,BUS),'tri',GREY)
# Puntos y materiales
L(P('PuntoRecepcion','b',x=80),P('PuntoMaterial','t',x=80),ORANGE)
L(P('Material','b',x=192),P('PuntoMaterial','t',x=128),ORANGE,via=470)
L(P('Material','b',x=240),P('ContenidoEducativo','t',x=240),BLUE)
L(P('Material','b',x=285),P('RegistroRecoleccion','t',x=362),BLUE,via=478)
L(P('Material','r',y=300),P('Campania','l',y=300),ORANGE,la='N',lb='N')
L(P('PuntoRecepcion','t',x=160),P('Campania','t',x=380),BLUE,via=243)
# Campañas
L(P('Campania','b',x=395),P('RegistroRecoleccion','t',x=395),BLUE,sym='diamond')
L(P('Campania','b',x=510),P('Participacion','t',x=510),ORANGE)
L(P('Campania','r',y=428),P('Apoyo','t',x=632),ORANGE)
L(P('Campania','r',y=448),P('Comentario','l',y=600),BLUE,via=[(592,448),(592,600)])
# Reportes
L(P('ReporteAmbiental','b',x=710),P('Apoyo','t',x=710),ORANGE)
L(P('ReporteAmbiental','b',x=794),P('Comentario','t',x=794),BLUE)
L(P('ReporteAmbiental','b',x=872),P('SeguimientoReporte','t',x=872),BLUE,sym='diamond')
D.legend(10,652,[('line',BLUE,'Relación 1:N'),('line',ORANGE,'Relación N:M'),('tri',GREY,'Herencia'),('dia',BLUE,'Composición')])
D.ax.add_patch(Rectangle((560,646),70,11,fc='#E6F0FA',ec='none'))
D.ax.text(565,651.8,'- autor: Usuario',fontsize=6.9,color=BLUE,fontweight='bold',va='center')
D.ax.text(636,652,'Referencia a Usuario, Municipio u Organización (1:N), indicada como atributo.',fontsize=7.4,va='center',color='#333333')
D.save('clases.png')
