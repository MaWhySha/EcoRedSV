from engine import *
# ================= PUNTOS =================
D=Diagram(650,432); b=D.boxes; L=D.link
T(D,'punto_recepcion',125,15,150)
T(D,'punto_material',355,70,145); T(D,'material',355,165,145); T(D,'contenido_educativo',355,275,145)
pr=b['punto_recepcion']['ry']
gbox(D,'municipio',8,pr['id_municipio'],90); gbox(D,'usuario',8,pr['id_gestor'],90)
gbox(D,'campania',545,pr['id_punto'],100)
gbox(D,'campania_material',545,b['material']['ry']['id_material'],100)
gbox(D,'registro_recoleccion',545,240,100)
L(rp(D,'municipio','r',y=pr['id_municipio']),rp(D,'punto_recepcion','l','id_municipio'),BLUE)
L(rp(D,'usuario','r',y=pr['id_gestor']),rp(D,'punto_recepcion','l','id_gestor'),BLUE)
L(rp(D,'usuario','b',x=45),rp(D,'contenido_educativo','l','id_autor'),BLUE)
L(rp(D,'punto_recepcion','r','id_punto'),rp(D,'campania','l',y=pr['id_punto']),BLUE)
L(rp(D,'punto_recepcion','r','id_punto'),rp(D,'punto_material','l','id_punto'),ORANGE,via=312,la='')
L(rp(D,'material','l','id_material'),rp(D,'punto_material','l','id_material'),ORANGE,via=336)
L(rp(D,'material','l','id_material'),rp(D,'contenido_educativo','l','id_material'),BLUE,via=336,la='')
L(rp(D,'material','r','id_material'),rp(D,'campania_material','l',y=b['material']['ry']['id_material']),ORANGE)
L(rp(D,'material','r','id_material'),rp(D,'registro_recoleccion','l',y=240),BLUE,via=522,la='')
mlegend(D,420); D.save('mod_puntos.png')

# ================= CAMPAÑAS =================
D=Diagram(650,392); b=D.boxes; L=D.link
T(D,'campania',140,15,150)
T(D,'campania_material',355,15,150); T(D,'registro_recoleccion',355,95,150); T(D,'participacion',355,230,150)
c=b['campania']['ry']
gbox(D,'municipio',8,120,95); gbox(D,'organizacion',8,155,95); gbox(D,'punto_recepcion',8,c['id_punto'],95); gbox(D,'usuario',8,232,95)
L(rp(D,'municipio','r',y=120),rp(D,'campania','l','id_municipio'),BLUE,via=118)
L(rp(D,'organizacion','r',y=155),rp(D,'campania','l','id_organizacion'),BLUE,via=126)
L(rp(D,'punto_recepcion','r',y=c['id_punto']),rp(D,'campania','l','id_punto'),BLUE)
L(rp(D,'usuario','r',y=232),rp(D,'campania','l','id_creador'),BLUE,via=114)
cm=b['campania_material']['ry']; rr=b['registro_recoleccion']['ry']; pa=b['participacion']['ry']
L(rp(D,'campania','r','id_campania'),rp(D,'campania_material','l','id_campania'),ORANGE,via=322)
L(rp(D,'campania','r','id_campania'),rp(D,'registro_recoleccion','l','id_campania'),BLUE,via=322,la='')
L(rp(D,'campania','r','id_campania'),rp(D,'participacion','l','id_campania'),ORANGE,via=322,la='')
gbox(D,'material',545,cm['id_material'],100); gbox(D,'usuario ',545,rr['id_registrado_por'],100)
L(rp(D,'material','l',y=cm['id_material']),rp(D,'campania_material','r','id_material'),ORANGE)
L(rp(D,'material','l',y=cm['id_material']),rp(D,'registro_recoleccion','r','id_material'),BLUE,via=525,la='')
L(rp(D,'usuario ','l',y=rr['id_registrado_por']),rp(D,'registro_recoleccion','r','id_registrado_por'),BLUE)
L(rp(D,'usuario ','l',y=rr['id_registrado_por']),rp(D,'participacion','r','id_usuario'),ORANGE,via=530,la='')
gbox(D,'apoyo',175,300,100); gbox(D,'comentario',175,335,100)
L(rp(D,'campania','r','id_campania'),rp(D,'apoyo','r',y=300),ORANGE,via=[(322,c['id_campania']),(322,300)],la='')
L(rp(D,'campania','r','id_campania'),rp(D,'comentario','r',y=335),BLUE,via=[(322,c['id_campania']),(322,335)],la='')
mlegend(D,380); D.save('mod_campanias.png')

# ================= REPORTES =================
D=Diagram(650,420); b=D.boxes; L=D.link
T(D,'reporte_ambiental',135,15,150)
T(D,'seguimiento_reporte',350,15,150); T(D,'apoyo',350,150,150); T(D,'comentario',350,262,150)
r=b['reporte_ambiental']['ry']; sg=b['seguimiento_reporte']['ry']; ap=b['apoyo']['ry']; co=b['comentario']['ry']
gbox(D,'municipio',8,r['id_municipio'],95); gbox(D,'usuario',8,r['id_autor'],95)
L(rp(D,'municipio','r',y=r['id_municipio']),rp(D,'reporte_ambiental','l','id_municipio'),BLUE)
L(rp(D,'usuario','r',y=r['id_autor']),rp(D,'reporte_ambiental','l','id_autor'),BLUE)
L(rp(D,'reporte_ambiental','r','id_reporte'),rp(D,'seguimiento_reporte','l','id_reporte'),BLUE,via=316)
L(rp(D,'reporte_ambiental','r','id_reporte'),rp(D,'apoyo','l','id_reporte'),ORANGE,via=316,la='')
L(rp(D,'reporte_ambiental','r','id_reporte'),rp(D,'comentario','l','id_reporte'),BLUE,via=316,la='')
gbox(D,'usuario ',545,sg['id_responsable'],100); gbox(D,'campania',545,368,100)
# campaña primero (pasa por encima)
L(rp(D,'usuario ','l',y=sg['id_responsable']),rp(D,'seguimiento_reporte','r','id_responsable'),BLUE)
L(rp(D,'usuario ','l',y=sg['id_responsable']),rp(D,'apoyo','r','id_usuario'),ORANGE,via=520,la='')
L(rp(D,'usuario ','l',y=sg['id_responsable']),rp(D,'comentario','r','id_usuario'),BLUE,via=520,la='')
# puente
D.ax.plot([520,520],[ap['id_campania']-4,ap['id_campania']+4],color='white',lw=4,zorder=2.5)
L(rp(D,'campania','l',y=368),rp(D,'apoyo','r','id_campania'),ORANGE,via=533)
L(rp(D,'campania','l',y=368),rp(D,'comentario','r','id_campania'),BLUE,via=533,la='')
mlegend(D,408); D.save('mod_reportes.png')
