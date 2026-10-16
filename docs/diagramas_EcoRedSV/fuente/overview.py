from engine import *
D=Diagram(900,450)
D.area(10,10,285,310,'Puntos y materiales','#EEF6F1')
D.area(305,10,290,310,'Campañas','#FBF4EA')
D.area(605,10,285,310,'Reportes y participación','#F4F0F8')
D.area(10,332,880,78,'Usuarios','#EEF3F9')
U,M,Og='usuario','municipio','organización'
nbox(D,'punto_recepcion',85,55,chips=(U,M))
nbox(D,'punto_material',85,125)
nbox(D,'material',85,195)
nbox(D,'contenido_educativo',85,265,w=128,chips=(U,))
nbox(D,'campania',455,55,chips=(U,M,Og),w=140)
nbox(D,'campania_material',385,195,w=128)
nbox(D,'participacion',525,125,chips=(U,))
nbox(D,'registro_recoleccion',455,265,w=132,chips=(U,))
nbox(D,'reporte_ambiental',680,55,w=132,chips=(U,M))
nbox(D,'seguimiento_reporte',680,125,w=136,chips=(U,))
nbox(D,'apoyo',815,195,chips=(U,))
nbox(D,'comentario',815,265,chips=(U,))
nbox(D,'municipio',230,372); nbox(D,'organizacion',670,372); nbox(D,'usuario',450,372)
b=D.boxes
def pt(n,side,t=0.5):
    B=b[n]
    if side=='l': return (B['x'],B['y']+t*B['h'],'l')
    if side=='r': return (B['x']+B['w'],B['y']+t*B['h'],'r')
    if side=='t': return (B['x']+t*B['w'],B['y'],'t')
    return (B['x']+t*B['w'],B['y']+B['h'],'b')
L=D.link
# Puntos
L(pt('punto_recepcion','b'),pt('punto_material','t'),ORANGE)
L(pt('material','t'),pt('punto_material','b'),ORANGE)
L(pt('material','b'),pt('contenido_educativo','t'),BLUE)
# hacia campañas
L(pt('punto_recepcion','r'),pt('campania','l'),BLUE)
L(pt('material','r',0.5),pt('campania_material','l'),ORANGE)
L(pt('material','r',0.8),pt('registro_recoleccion','l',0.5),BLUE,via=260)
# campañas internas
L(pt('campania','b',(400-385)/140),pt('campania_material','t',(400-321)/128),ORANGE)
L(pt('campania','b',(510-385)/140),pt('participacion','t',(510-463)/124),ORANGE)
L(pt('campania','b',0.5),pt('registro_recoleccion','t',0.5),BLUE)
# reportes
L(pt('reporte_ambiental','b'),pt('seguimiento_reporte','t'),BLUE)
L(pt('reporte_ambiental','r',0.3),pt('apoyo','t',0.5),BLUE if False else ORANGE)
L(pt('reporte_ambiental','r',0.7),(875,b['comentario']['y']+0.5*b['comentario']['h'],'r'),BLUE,via=[(875,b['reporte_ambiental']['y']+0.7*b['reporte_ambiental']['h'])])
# campañas -> apoyo / comentario
L(pt('campania','r',0.3),pt('apoyo','l'),ORANGE,via=[(600,b['campania']['y']+0.3*b['campania']['h']),(600,195)])
L(pt('campania','r',0.7),pt('comentario','l'),BLUE,via=[(590,b['campania']['y']+0.7*b['campania']['h']),(590,265)])
# usuarios
L(pt('municipio','r'),pt('usuario','l'),BLUE)
L(pt('organizacion','l'),pt('usuario','r'),BLUE)
D.legend(15,432,[('line',BLUE,'Uno a muchos (1:N)'),('line',ORANGE,'Forma parte de una relación muchos a muchos (N:M)')])
D.ax.text(885,432,'Etiquetas blancas: la tabla tiene una clave foránea hacia usuario, municipio u organización (1:N).',fontsize=7.4,ha='right',va='center',color='#333333')
D.save('overview.png')
