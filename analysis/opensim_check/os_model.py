import json,numpy as np,opensim as osim
from scipy.spatial.transform import Rotation as Rot
G=json.load(open('geom.json')); mm=1e-3; Rw=G['R']*mm
S0=np.array(G['S0'])/np.linalg.norm(G['S0']); down=np.array([0,-1,0.])
def align(a,b):
    v=np.cross(a,b); c=a@b
    K=np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]]); return np.eye(3)+K+K@K/(1+c)
Ral=align(S0,down)                       # template humerus -> arm hanging down (same as the app)
beta=np.radians(30); k=np.array([-np.sin(beta),0,-np.cos(beta)])   # abduction axis of the app (plane 30 deg)
# frame whose z axis is k
x=np.cross([0,1,0],k); x/=np.linalg.norm(x); y=np.cross(k,x); Rf=np.column_stack([x,y,k])
eul=Rot.from_matrix(Rf).as_euler('XYZ')
model=osim.Model(); model.setName('gh_from_app'); model.setGravity(osim.Vec3(0,-9.81,0))
gr=model.getGround()
hum=osim.Body('humerus',2.0,osim.Vec3(0,-0.15,0),osim.Inertia(0.02,0.002,0.02)); model.addBody(hum)
pf=osim.PhysicalOffsetFrame('pf',gr,osim.Transform()); pf.set_orientation(osim.Vec3(*eul)); gr.addComponent(pf)
cf=osim.PhysicalOffsetFrame('cf',hum,osim.Transform()); cf.set_orientation(osim.Vec3(*eul)); hum.addComponent(cf)
j=osim.PinJoint('gh',pf,cf); model.addJoint(j)
coord=j.upd_coordinates(0); coord.setName('abd')
ws=osim.WrapSphere(); ws.setName('head'); ws.set_radius(Rw); ws.set_translation(osim.Vec3(0,0,0)); hum.addWrapObject(ws)
def v3(a): return osim.Vec3(*[float(t) for t in a])
# graft: tension-free path spring between SG (scapula) and GT (humerus) wrapping over the head
SG=np.array(G['SG'])*mm; GT=Ral@(np.array(G['GT'])*mm)
gp=osim.PathSpring('graft',0.04,100.0,0.0); gp.updGeometryPath().appendNewPathPoint('SG',gr,v3(SG)); gp.updGeometryPath().appendNewPathPoint('GT',hum,v3(GT)); gp.updGeometryPath().addPathWrap(ws); model.addForce(gp)
mus={}
for name,d in G['muscles'].items():
    if name in('sh','tlh','tmaj','cbr'): continue
    a=osim.PathActuator(); a.setName(name); a.set_optimal_force(1.0)
    a.updGeometryPath().appendNewPathPoint('o',gr,v3(np.array(d['origin'])*mm)); a.updGeometryPath().appendNewPathPoint('i',hum,v3(Ral@(np.array(d['insertion'])*mm))); a.updGeometryPath().addPathWrap(ws); model.addForce(a); mus[name]=a
st=model.initSystem()
c=model.getCoordinateSet().get('abd')
ang=np.arange(0,121); Lg=[]; M={n:[] for n in mus}; LM={n:[] for n in mus}
for e in ang:
    c.setValue(st,np.radians(e)); model.realizePosition(st); Lg.append(gp.getLength(st)/mm)
    for n,a in mus.items(): LM[n].append(a.getLength(st)/mm); M[n].append(a.computeMomentArm(st,c)/mm)
Lg=np.array(Lg); app=np.array(G['app']['lhbt'])
print('OpenSim',osim.GetVersionAndDate().split(',')[0] if False else '4.6')
print('GRAFT PATH (SG->GT over the head sphere): OpenSim vs app wrapPath')
for e in (0,10,30,45,60,90,120): print('  %3d deg  OpenSim %.2f mm   app %.2f mm   diff %+.2f'%(e,Lg[e],app[e],Lg[e]-app[e]))
d=Lg-app; print('  max |diff| %.2f mm, mean diff %+.2f mm, RMSE %.2f mm (path 0-60 deg)'%(np.abs(d[:61]).max(),d[:61].mean(),np.sqrt((d[:61]**2).mean())))
print('\nMUSCLE path length change from 0 deg (%) and moment arm about the abduction axis (mm), OpenSim path with head wrapping')
for n in mus:
    L0=LM[n][0]; print('  %-4s L0 %5.0f mm | length %% at 30/60/90: %+.0f %+.0f %+.0f | moment arm at 0/30/60/90: %+.1f %+.1f %+.1f %+.1f'%(n,L0,*[(LM[n][t]/L0-1)*100 for t in (30,60,90)],*[M[n][t] for t in (0,30,60,90)]))
json.dump({'graft_opensim':Lg.tolist(),'graft_app':app.tolist(),'muscle_len':LM,'moment_arm':M},open('os_results.json','w'))
model.printToXML('gh_from_app.osim')
