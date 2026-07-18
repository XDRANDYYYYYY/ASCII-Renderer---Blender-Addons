import math
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

LIGHT_INT = " .:-=+*#%@" # intensity of light for ASCII paints, differenating dark and lights

def shade(p,n,li):
    # for one point, calculate the intensity from all the light source
    # Lambertian Reflectance
    Sum=0.0
    for l in li:
        if l['TYPE']=='SUN':
            a=-l['DIR']
            b=l['E']
        else:
            a=l['POS']-p
            a2=(a).dot(a)
            if a2<1e-9:
                continue
            b=l['E']/(4.0*math.pi*a2)
            a=a/math.sqrt(a2)
        if n.dot(a)>0.0:
            Sum+=n.dot(a)*b
    return Sum

def inten(g,z,w,h):
    a=sorted(g[i] for i in range(w*h) if z[i]!=float('inf'))
    if not a:
        return [' ']*(w*h)
    c=[' ']*(w*h)
    for i in range(w*h):
        if z[i]==float('inf'):
            continue
        c[i]=LIGHT_INT[max(1, min(9,1+int(max(0.0,min((g[i]-a[0])/(a[-1]-a[0]),1.0))*(9)+0.5)))]
    return c
def render(context,w,h):
    g=[0]*(w*h)
    z=[float('inf')]*(w*h)
    if context.scene.camera is None:
        raise RuntimeError("No active camera detected")
    l=[]
    for obj in context.scene.objects:
        if obj.type=='LIGHT':
            data=obj.data
            l.append({
                'TYPE':data.type,
                'POS':obj.matrix_world.translation.copy(),
                'DIR':(obj.matrix_world.to_3x3()@Vector((0,0,-1))).normalized(),
                'E':data.energy,
        })
    if not l:
        l=[{'TYPE':'SUN','POS':context.scene.camera.matrix_world.translation,'DIR':(context.scene.camera.matrix_world.to_3x3()@Vector((0,0,-1))).normalized(),'E':1.0}]
    for obj in context.scene.objects:
        if obj.type!='MESH':
            continue
        tem=obj.evaluated_get(context.evaluated_depsgraph_get())
        m=tem.to_mesh()
        n=tem.matrix_world.inverted().transposed().to_3x3()
        real=[]
        for v in m.vertices:
            real.append(tem.matrix_world@v.co) # Real location info of an objects in the scene
        _2dpos=[]
        for i in real:
            _2dpos.append(world_to_camera_view(context.scene,context.scene.camera,i))
        for p in m.polygons:
            for k in range(1,len(p.vertices)-1):
                # If the z compent of vertcies on camera position is negative (behind camera), then skip it
                if _2dpos[p.vertices[0]][2]<=0 or _2dpos[p.vertices[k]][2]<=0 or _2dpos[p.vertices[k+1]][2]<=0:
                    continue
                q0=real[p.vertices[0]]
                q1=real[p.vertices[k]]
                q2=real[p.vertices[k+1]]
                if (n@p.normal).normalized().dot(((q0+q1+q2)/3.0-context.scene.camera.matrix_world.translation).normalized())>0: # If this triangle facing the samge direction with camera, skip it(behind of this triangle will not be seen)
                    continue
                sx0=_2dpos[p.vertices[0]][0]*w
                sx1=_2dpos[p.vertices[k]][0]*w
                sx2=_2dpos[p.vertices[k+1]][0]*w
                sy0=(1.0-_2dpos[p.vertices[0]][1])*h
                sy1=(1.0-_2dpos[p.vertices[k]][1])*h
                sy2=(1.0-_2dpos[p.vertices[k+1]][1])*h
                sz0=_2dpos[p.vertices[0]][2]
                sz1=_2dpos[p.vertices[k]][2]
                sz2=_2dpos[p.vertices[k+1]][2] # Position in actual render grid
                min_x=max(int(min(sx0,sx1,sx2)),0)
                max_x=min(int(max(sx0,sx1,sx2))+1,w-1)
                min_y=max(int(min(sy0,sy1,sy2)),0)
                max_y=min(int(max(sy0,sy1,sy2))+1,h-1) # The grid occupied by triangle
                if (min_x>max_x)or(min_y>max_y):
                    continue
                for i in range(min_y,max_y+1):
                    for j in range(min_x,max_x+1):
                        px,py=j+0.5,i+0.5 # Refer the center, adding 0.5 would make the "pixel" shift less
                        w0=((sy1-sy2)*(px-sx2)+(sx2-sx1)*(py-sy2))/((sy1-sy2)*(sx0-sx2)+(sx2-sx1)*(sy0-sy2))
                        w1=((sy2-sy0)*(px-sx2)+(sx0-sx2)*(py-sy2))/((sy1-sy2)*(sx0-sx2)+(sx2-sx1)*(sy0-sy2))
                        w2=1-w0-w1
                        if w0<0 or w1<0 or w2<0:
                            continue
                        if w0*sz0+w1*sz1+w2*sz2>=z[j+i*w]: # If it was behind an triangle that was processed before
                            continue
                        z[j+i*w]=w0*sz0+w1*sz1+w2*sz2
                        g[j+i*w]=shade(w0*q0+w1*q1+w2*q2,(n@p.normal).normalized(),l)

        tem.to_mesh_clear()
    c=inten(g,z,w,h)
    lines=[]
    for row in range(h):
        lines.append(''.join(c[row*w:(row+1) * w]))
    return '\n'.join(lines)
