from engine import *
D=Diagram(650,262)
glist(D,'gm',8,15,120,'Referencian a municipio',['punto_recepcion','campania','reporte_ambiental'])
glist(D,'go',8,100,120,'Referencian a organización',['campania'])
T(D,'municipio',158,15,122); T(D,'organizacion',158,100,122); T(D,'usuario',318,15,148)
glist(D,'gu',480,15,166,'Referencian a usuario',[
 'punto_recepcion (id_gestor)','campania (id_creador)','participacion (id_usuario)','registro_recoleccion (id_registrado_por)',
 'reporte_ambiental (id_autor)','seguimiento_reporte (id_responsable)','apoyo (id_usuario)','comentario (id_usuario)','contenido_educativo (id_autor)'])
L=D.link; b=D.boxes
L(rp(D,'municipio','r','id_municipio'),rp(D,'usuario','l','id_municipio'),BLUE,via=300)
L(rp(D,'organizacion','r','id_organizacion'),rp(D,'usuario','l','id_organizacion'),BLUE,via=290)
L(rp(D,'usuario','r','id_usuario'),rp(D,'gu','l',y=b['usuario']['ry']['id_usuario']),BLUE)
L(rp(D,'municipio','l','id_municipio'),rp(D,'gm','r',y=b['municipio']['ry']['id_municipio']),BLUE)
L(rp(D,'organizacion','l','id_organizacion'),rp(D,'go','r',y=b['organizacion']['ry']['id_organizacion']),BLUE)
mlegend(D,250)
D.save('mod_usuarios.png')
