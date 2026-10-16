import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Polygon
from matplotlib import font_manager as fm
fm.fontManager.addfont('/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf')
fm.fontManager.addfont('/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf')
for f in ['Carlito-Italic.ttf','Carlito-BoldItalic.ttf']:
    try: fm.fontManager.addfont('/usr/share/fonts/truetype/crosextra/'+f)
    except Exception: pass
plt.rcParams['font.family']='Carlito'

DARK='#2F6B4F'; PKBG='#E3F1E8'; LINE='#2F6B4F'; GH='#F1F3F2'; GHE='#A7B3AC'; GHT='#4E5A54'
BLUE='#2B78C2'; ORANGE='#E07B1F'; GREY='#7A7A7A'
HH=19; RH=13.5; FS=7.6

class Diagram:
    def __init__(s, W, H):
        s.W,s.H=W,H
        s.fig=plt.figure(figsize=(W/100,H/100),dpi=300)
        s.ax=s.fig.add_axes([0,0,1,1]); s.ax.set_xlim(0,W); s.ax.set_ylim(H,0); s.ax.axis('off')
        s.boxes={}
    def area(s,x,y,w,h,label,fill):
        s.ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0,rounding_size=8',fc=fill,ec='#D3DED7',lw=0.8,zorder=0))
        s.ax.text(x+8,y+h-7,label,fontsize=8.5,fontweight='bold',color=DARK,va='bottom',zorder=1)
    def table(s,name,x,y,w,rows):
        h=HH+RH*len(rows)+3
        ax=s.ax
        ax.add_patch(Rectangle((x,y),w,h,fc='white',ec=LINE,lw=0.9,zorder=3))
        ax.add_patch(Rectangle((x,y),w,HH,fc=DARK,ec=LINE,lw=0.9,zorder=3))
        ax.text(x+w/2,y+HH/2+0.5,name,ha='center',va='center',color='white',fontsize=8.2,fontweight='bold',zorder=4)
        ry={}
        for i,(k,t) in enumerate(rows):
            yc=y+HH+1.5+RH*i+RH/2
            if k=='PK':
                ax.add_patch(Rectangle((x+0.5,yc-RH/2),w-1,RH,fc=PKBG,ec='none',zorder=3))
                ax.text(x+6,yc,'PK',fontsize=6.8,fontweight='bold',color=DARK,va='center',zorder=4)
                ax.text(x+24,yc,t,fontsize=FS,fontweight='bold',va='center',zorder=4)
            elif k=='FK':
                ax.text(x+6,yc,'FK',fontsize=6.8,fontweight='bold',color=BLUE,va='center',zorder=4)
                ax.text(x+24,yc,t,fontsize=FS,style='italic',va='center',zorder=4)
            else:
                ax.text(x+24,yc,t,fontsize=FS,va='center',color='#222222',zorder=4)
            ry[t]=yc
        b=dict(x=x,y=y,w=w,h=h,ry=ry); s.boxes[name]=b; return b
    def ghost(s,name,x,y,w,sub=None):
        h=20 if not sub else 31
        s.ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0,rounding_size=3',fc=GH,ec=GHE,lw=0.8,zorder=3))
        s.ax.text(x+w/2,y+(10 if sub else h/2)+0.5,name,ha='center',va='center',fontsize=7.8,fontweight='bold',color=GHT,zorder=4)
        if sub: s.ax.text(x+w/2,y+22,sub,ha='center',va='center',fontsize=6.6,color=GHT,style='italic',zorder=4)
        b=dict(x=x,y=y,w=w,h=h,ry={}); s.boxes[name]=b; return b
    def cls(s,name,x,y,w,attrs,meths,stereo=None,assoc=False):
        lh=11.2; ax=s.ax
        hh=HH+(9 if stereo else 0)
        h=hh+4+lh*len(attrs)+(6+lh*len(meths) if meths else 0)+3
        ax.add_patch(Rectangle((x,y),w,h,fc='#F6FBF8' if stereo else 'white',ec=LINE,lw=0.9,zorder=3))
        hc='#A9D3BC' if stereo else ('#5E9C7C' if assoc else DARK)
        ax.add_patch(Rectangle((x,y),w,hh,fc=hc,ec=LINE,lw=0.9,zorder=3))
        if stereo:
            ax.text(x+w/2,y+8,'«abstracta»',ha='center',va='center',fontsize=6.6,color='#1F3F2E',zorder=4)
            ax.text(x+w/2,y+19,name,ha='center',va='center',fontsize=8.4,fontweight='bold',style='italic',color='#1F3F2E',zorder=4)
        else:
            ax.text(x+w/2,y+hh/2+0.5,name,ha='center',va='center',fontsize=8.4,fontweight='bold',color='white',zorder=4)
        yy=y+hh+3
        for a in attrs:
            ax.text(x+5,yy+lh/2,a,fontsize=6.9,va='center',color='#222222',zorder=4); yy+=lh
        if meths:
            yy+=2; ax.plot([x,x+w],[yy,yy],color=LINE,lw=0.6,zorder=4); yy+=3
            for m in meths:
                ax.text(x+5,yy+lh/2,m,fontsize=6.9,va='center',color='#222222',style='italic' if stereo and 'obtener' in m or (stereo and 'mostrar' in m) or (stereo and 'validar' in m) else 'normal',zorder=4); yy+=lh
        b=dict(x=x,y=y,w=w,h=h,ry={}); s.boxes[name]=b; return b
    # ---------- anclajes ----------
    def P(s,name,side,t=0.5,row=None):
        b=s.boxes[name]
        if side in 'lr':
            yv=b['ry'][row] if row else b['y']+t*b['h']
            return (b['x'] if side=='l' else b['x']+b['w'], yv, side)
        xv=b['x']+t*b['w']
        return (xv, b['y'] if side=='t' else b['y']+b['h'], side)
    def link(s,a,b,color,la='1',lb='N',via=None,sym=None,lw=1.5,lpos=None):
        (x1,y1,s1),(x2,y2,s2)=a,b
        if via=='direct': pts=[(x1,y1),(x2,y2)]
        elif isinstance(via,list): pts=[(x1,y1)]+via+[(x2,y2)]
        elif s1 in 'lr' and s2 in 'lr':
            if abs(y1-y2)<0.5: pts=[(x1,y1),(x2,y2)]
            else:
                mx=via if via is not None else (x1+x2)/2
                pts=[(x1,y1),(mx,y1),(mx,y2),(x2,y2)]
        elif s1 in 'tb' and s2 in 'tb':
            if abs(x1-x2)<0.5: pts=[(x1,y1),(x2,y2)]
            else:
                my=via if via is not None else (y1+y2)/2
                pts=[(x1,y1),(x1,my),(x2,my),(x2,y2)]
        elif s1 in 'lr': pts=[(x1,y1),(x2,y1),(x2,y2)]
        else: pts=[(x1,y1),(x1,y2),(x2,y2)]
        xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
        s.ax.plot(xs,ys,color=color,lw=lw,solid_joinstyle='round',solid_capstyle='butt',zorder=2)
        def lab(p0,p1,txt,side_):
            import math
            dx,dy=p1[0]-p0[0],p1[1]-p0[1]; L=math.hypot(dx,dy) or 1; ux,uy=dx/L,dy/L
            off=9 if txt in('1','N') else 9
            px,py=p0[0]+ux*off, p0[1]+uy*off
            nx,ny=-uy,ux
            px+=nx*6.5; py+=ny*6.5
            s.ax.text(px,py,txt,fontsize=8,fontweight='bold',color=color,ha='center',va='center',zorder=6)
        if la:
            if sym=='diamond':
                import math
                p0,p1=pts[0],pts[1]; dx,dy=p1[0]-p0[0],p1[1]-p0[1]; L_=math.hypot(dx,dy) or 1
                s.ax.text(p0[0]+dx/L_*20-dy/L_*7,p0[1]+dy/L_*20+dx/L_*7,la,fontsize=8,fontweight='bold',color=color,ha='center',va='center',zorder=6)
            else: lab(pts[0],pts[1],la,s1)
        if lb: lab(pts[-1],pts[-2],lb,s2)
        if sym: s._sym(pts[0],pts[1],sym,color)
    def _sym(s,p0,p1,kind,color):
        import math
        dx,dy=p1[0]-p0[0],p1[1]-p0[1]; L=math.hypot(dx,dy) or 1; ux,uy=dx/L,dy/L; nx,ny=-uy,ux
        if kind=='diamond':
            p0=(p0[0],p0[1]); a=p0; b=(p0[0]+ux*7,p0[1]+uy*7+0); c=(p0[0]+ux*14,p0[1]+uy*14); d=(p0[0]+ux*7,p0[1]+uy*7)
            pts=[a,(b[0]+nx*4.5,b[1]+ny*4.5),c,(d[0]-nx*4.5,d[1]-ny*4.5)]
            s.ax.add_patch(Polygon(pts,closed=True,fc=color,ec=color,lw=0.8,zorder=5))
        if kind=='tri':
            p0=(p0[0],p0[1]); a=p0; base=(p0[0]+ux*12,p0[1]+uy*12)
            pts=[a,(base[0]+nx*6.5,base[1]+ny*6.5),(base[0]-nx*6.5,base[1]-ny*6.5)]
            s.ax.add_patch(Polygon(pts,closed=True,fc='white',ec=color,lw=1.1,zorder=5))
    def inherit(s,child_pt,parent_pt,via=None):
        # línea gris con triángulo en el padre
        (x1,y1,s1),(x2,y2,s2)=parent_pt,child_pt
        self=s
        if via is None: pts=[(x1,y1),(x1,(y1+y2)/2),(x2,(y1+y2)/2),(x2,y2)] if abs(x1-x2)>0.5 else [(x1,y1),(x2,y2)]
        else: pts=[(x1,y1)]+via+[(x2,y2)]
        s.ax.plot([p[0] for p in pts],[p[1] for p in pts],color=GREY,lw=1.3,zorder=2,solid_joinstyle='round')
        s._sym(pts[0],pts[1],'tri',GREY)
    def legend(s,x,y,items):
        cx=x
        for kind,color,text in items:
            if kind=='line':
                s.ax.plot([cx,cx+22],[y,y],color=color,lw=2,zorder=6); s.ax.text(cx+11,y-6,'1   N' if 'N:M' not in text else 'N   N',fontsize=6,ha='center',color=color,fontweight='bold')
                cx+=28
            elif kind=='tri':
                s.ax.plot([cx,cx+22],[y,y],color=GREY,lw=1.3,zorder=6); s._sym((cx+22,y),(cx,y),'tri',GREY); cx+=28
            elif kind=='dia':
                s.ax.plot([cx,cx+22],[y,y],color=BLUE,lw=1.5,zorder=6); s._sym((cx,y),(cx+22,y),'diamond',BLUE); cx+=28
            elif kind=='ghost':
                s.ax.add_patch(FancyBboxPatch((cx,y-6),22,12,boxstyle='round,pad=0,rounding_size=2',fc=GH,ec=GHE,lw=0.8)); cx+=28
            t=s.ax.text(cx,y,text,fontsize=7.6,va='center',color='#333333')
            s.fig.canvas.draw(); bb=t.get_window_extent(); w=bb.width/s.fig.dpi*100
            cx+=w+18
    def save(s,path):
        s.fig.savefig(path,dpi=300,facecolor='white'); plt.close(s.fig)

def namebox(D,name,cx,cy,w=128,h=26,fill=DARK):
    x,y=cx-w/2,cy-h/2
    D.ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0,rounding_size=4',fc=fill,ec=fill,lw=0.8,zorder=3))
    D.ax.text(cx,cy+0.5,name,ha='center',va='center',fontsize=8.6,fontweight='bold',color='white',zorder=4)
    D.boxes[name]=dict(x=x,y=y,w=w,h=h,ry={},cx=cx,cy=cy)

def straight(D,a,b,color,la='1',lb='N',lw=1.6):
    import math
    A,B=D.boxes[a],D.boxes[b]
    def clip(box,tx,ty):
        cx,cy=box['cx'],box['cy']; dx,dy=tx-cx,ty-cy
        sx=(box['w']/2)/abs(dx) if dx else 1e9; sy=(box['h']/2)/abs(dy) if dy else 1e9
        t=min(sx,sy); return cx+dx*t, cy+dy*t
    p1=clip(A,B['cx'],B['cy']); p2=clip(B,A['cx'],A['cy'])
    D.ax.plot([p1[0],p2[0]],[p1[1],p2[1]],color=color,lw=lw,zorder=2,solid_capstyle='round')
    dx,dy=p2[0]-p1[0],p2[1]-p1[1]; L=math.hypot(dx,dy); ux,uy=dx/L,dy/L; nx,ny=-uy,ux
    for (px,py),txt,sg in [(p1,la,1),(p2,lb,-1)]:
        qx,qy=px+ux*10*sg+nx*7, py+uy*10*sg+ny*7
        D.ax.text(qx,qy,txt,fontsize=8.2,fontweight='bold',color=color,ha='center',va='center',zorder=6,
                  bbox=dict(boxstyle='round,pad=0.12',fc='white',ec='none',alpha=0.9))

def nbox(D,name,cx,cy,w=124,chips=(),h=None):
    h=h or (36 if chips else 26)
    x,y=cx-w/2,cy-h/2
    D.ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0,rounding_size=4',fc=DARK,ec=DARK,lw=0.8,zorder=3))
    ty=y+(11 if chips else h/2)+0.5
    D.ax.text(cx,ty,name,ha='center',va='center',fontsize=8.6,fontweight='bold',color='white',zorder=4)
    if chips:
        # medir y centrar
        widths=[len(c)*3.55+8 for c in chips]; tot=sum(widths)+4*(len(chips)-1); sx=cx-tot/2
        for c,wc in zip(chips,widths):
            D.ax.add_patch(FancyBboxPatch((sx,y+20),wc,11,boxstyle='round,pad=0,rounding_size=5',fc='white',ec='white',lw=0.5,zorder=4))
            D.ax.text(sx+wc/2,y+25.8,c,ha='center',va='center',fontsize=6.4,color=BLUE,fontweight='bold',zorder=5)
            sx+=wc+4
    D.boxes[name]=dict(x=x,y=y,w=w,h=h,ry={},cx=cx,cy=cy)

def ref_chips(D,x,y,w,chips):
    widths=[len(c)*3.5+10 for c in chips]; tot=sum(widths)+4*(len(chips)-1); sx=x+w/2-tot/2
    for c,wc in zip(chips,widths):
        D.ax.add_patch(FancyBboxPatch((sx,y),wc,10.5,boxstyle='round,pad=0,rounding_size=5',fc='#E6F0FA',ec='#B9D3EE',lw=0.6,zorder=5))
        D.ax.text(sx+wc/2,y+5.4,c,ha='center',va='center',fontsize=6.2,color=BLUE,fontweight='bold',zorder=6)
        sx+=wc+4

def cbox(D,name,x,y,w,attrs,meths,stereo=False,assoc=False,chips=()):
    ax=D.ax; lh=11.2
    hh=HH+(9 if stereo else 0)
    ch=14 if chips else 0
    h=hh+ch+4+lh*len(attrs)+((6+lh*len(meths)) if meths else 0)+3
    ax.add_patch(Rectangle((x,y),w,h,fc='#F6FBF8' if stereo else 'white',ec=LINE,lw=0.9,zorder=3))
    hc='#A9D3BC' if stereo else ('#5E9C7C' if assoc else DARK)
    ax.add_patch(Rectangle((x,y),w,hh,fc=hc,ec=LINE,lw=0.9,zorder=3))
    if stereo:
        ax.text(x+w/2,y+8,'«abstracta»',ha='center',va='center',fontsize=6.6,color='#1F3F2E',zorder=4)
        ax.text(x+w/2,y+19.5,name,ha='center',va='center',fontsize=8.6,fontweight='bold',style='italic',color='#1F3F2E',zorder=4)
    else:
        ax.text(x+w/2,y+hh/2+0.5,name,ha='center',va='center',fontsize=8.6,fontweight='bold',color='white',zorder=4)
    yy=y+hh
    if chips:
        ref_chips(D,x,yy+2,w,chips); yy+=ch
    yy+=3
    for a in attrs:
        ax.text(x+5,yy+lh/2,a,fontsize=6.9,va='center',color='#222222',zorder=4); yy+=lh
    if meths:
        yy+=2; ax.plot([x,x+w],[yy,yy],color=LINE,lw=0.6,zorder=4); yy+=3
        for m in meths:
            it = stereo and m.endswith('*')
            ax.text(x+5,yy+lh/2,m.rstrip('*'),fontsize=6.9,va='center',color='#222222',style='italic' if it else 'normal',zorder=4); yy+=lh
    D.boxes[name]=dict(x=x,y=y,w=w,h=h,ry={},cx=x+w/2,cy=y+h/2)
    return D.boxes[name]

def pt(D,n,side,t=0.5,row=None):
    B=D.boxes[n]
    if side in 'lr':
        yv=B['ry'][row] if row else B['y']+t*B['h']
        return (B['x'] if side=='l' else B['x']+B['w'], yv, side)
    return (B['x']+t*B['w'], B['y'] if side=='t' else B['y']+B['h'], side)

TBL={
 "municipio": [("PK","id_municipio"),("","nombre"),("","departamento")],
 "organizacion": [("PK","id_organizacion"),("","nombre"),("","tipo"),("","descripcion"),("","correo_contacto"),("","telefono_contacto"),("","creado_en")],
 "usuario": [("PK","id_usuario"),("","nombre_usuario"),("","correo"),("","correo_verificado"),("","contrasena"),("","nombre"),("","rol"),("FK","id_municipio"),("FK","id_organizacion"),("","activo"),("","fecha_registro")],
 "material": [("PK","id_material"),("","nombre"),("","categoria"),("","descripcion"),("","indicaciones")],
 "punto_recepcion": [("PK","id_punto"),("","nombre"),("","tipo"),("","direccion"),("","latitud"),("","longitud"),("FK","id_municipio"),("","horario"),("","condiciones_entrega"),("","telefono_contacto"),("","estado_informacion"),("FK","id_gestor"),("","activo"),("","creado_en"),("","actualizado_en")],
 "punto_material": [("PK","id_punto_material"),("FK","id_punto"),("FK","id_material"),("","observaciones")],
 "campania": [("PK","id_campania"),("","titulo"),("","descripcion"),("","fecha_inicio"),("","fecha_fin"),("","direccion"),("","latitud"),("","longitud"),("FK","id_municipio"),("","estado"),("FK","id_organizacion"),("FK","id_punto"),("FK","id_creador"),("","creado_en"),("","actualizado_en")],
 "campania_material": [("PK","id_campania_material"),("FK","id_campania"),("FK","id_material")],
 "participacion": [("PK","id_participacion"),("FK","id_usuario"),("FK","id_campania"),("","fecha_inscripcion"),("","asistio")],
 "registro_recoleccion": [("PK","id_registro"),("FK","id_campania"),("FK","id_material"),("","peso_kg"),("","fecha_registro"),("FK","id_registrado_por"),("","observaciones")],
 "reporte_ambiental": [("PK","id_reporte"),("","titulo"),("","descripcion"),("","direccion"),("","latitud"),("","longitud"),("FK","id_municipio"),("","gravedad"),("","estado"),("","visible"),("","fotografia"),("FK","id_autor"),("","fecha_reporte"),("","actualizado_en")],
 "seguimiento_reporte": [("PK","id_seguimiento"),("FK","id_reporte"),("FK","id_responsable"),("","estado_anterior"),("","estado_nuevo"),("","comentario"),("","fecha")],
 "apoyo": [("PK","id_apoyo"),("FK","id_usuario"),("FK","id_reporte"),("FK","id_campania"),("","fecha")],
 "comentario": [("PK","id_comentario"),("FK","id_usuario"),("FK","id_reporte"),("FK","id_campania"),("","texto"),("","visible"),("","fecha")],
 "contenido_educativo": [("PK","id_contenido"),("","titulo"),("","resumen"),("","contenido"),("FK","id_material"),("FK","id_autor"),("","publicado"),("","fecha_publicacion")],
}
def T(D,name,x,y,w,key=None):
    b=D.table(name,x,y,w,TBL[name]); return b
def rowy(y,i): return y+HH+1.5+RH*i+RH/2
def gbox(D,name,x,cy,w=100):
    D.ghost(name,x,cy-10,w); b=D.boxes[name]; b['cy']=cy; return b
def glist(D,key,x,y,w,title,lines):
    h=18+len(lines)*11.5+4
    D.ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0,rounding_size=3',fc=GH,ec=GHE,lw=0.8,zorder=3))
    D.ax.text(x+7,y+10,title,fontsize=7.4,fontweight='bold',color=GHT,va='center',zorder=4)
    for i,l in enumerate(lines):
        D.ax.text(x+9,y+22+i*11.5,l,fontsize=6.9,color=GHT,va='center',zorder=4)
    D.boxes[key]=dict(x=x,y=y,w=w,h=h,ry={})
def rp(D,n,side,field=None,y=None,x=None):
    B=D.boxes[n]
    if side in 'lr':
        yv = B['ry'][field] if field else (y if y is not None else B['y']+B['h']/2)
        return (B['x'] if side=='l' else B['x']+B['w'], yv, side)
    xv = x if x is not None else B['x']+B['w']/2
    return (xv, B['y'] if side=='t' else B['y']+B['h'], side)
def mlegend(D,y):
    D.legend(8,y,[('line',BLUE,'Uno a muchos (1:N)'),('line',ORANGE,'Parte de una relación N:M'),('ghost',None,'Tabla de otro módulo')])
