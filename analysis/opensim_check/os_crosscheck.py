# Cross-check of the shoulder app's graft path formula against OpenSim 4.6 (pip install opensim)
# Run after os_model.py (needs geom.json). The anchor is placed 0.5 mm outside the wrap sphere so that OpenSim wraps.
import json,numpy as np,opensim as osim
from scipy.spatial.transform import Rotation as Rot
exec(open('os_model.py').read().split("st=model.initSystem()")[0])
def rodr(ax,ang):
    ax=ax/np.linalg.norm(ax); K=np.array([[0,-ax[2],ax[1]],[ax[2],0,-ax[0]],[-ax[1],ax[0],0]]); return np.eye(3)+np.sin(ang)*K+(1-np.cos(ang))*K@K
def wrap(A,B,R):
    dA=np.linalg.norm(A); ea=A/dA; bd=B/np.linalg.norm(B); Bp=bd*R; al=np.arccos(np.clip(ea@bd,-1,1)); be=np.arccos(min(1,R/dA)) if dA>R else 0
    if al<=be: return np.linalg.norm(A-Bp)+np.linalg.norm(Bp-B)
    return np.sqrt(max(0,dA*dA-R*R))+R*(al-be)+np.linalg.norm(Bp-B)
A0=np.array(G['SG'])*mm; B0=np.array(G['GT'])*mm; Bin=Ral@B0; Bout=Bin/np.linalg.norm(Bin)*(Rw+0.0005)
def build(Bs):
    m=osim.Model(); m.setGravity(osim.Vec3(0,-9.81,0)); g=m.getGround()
    h=osim.Body('humerus',2.0,osim.Vec3(0,-0.15,0),osim.Inertia(0.02,0.002,0.02)); m.addBody(h)
    p=osim.PhysicalOffsetFrame('pf',g,osim.Transform()); p.set_orientation(osim.Vec3(*eul)); g.addComponent(p)
    c=osim.PhysicalOffsetFrame('cf',h,osim.Transform()); c.set_orientation(osim.Vec3(*eul)); h.addComponent(c)
    j=osim.PinJoint('gh',p,c); m.addJoint(j); j.upd_coordinates(0).setName('abd')
    w=osim.WrapSphere(); w.setName('head'); w.set_radius(Rw); w.set_translation(osim.Vec3(0,0,0)); h.addWrapObject(w)
    s=osim.PathSpring('graft',0.04,100.0,0.0); s.updGeometryPath().appendNewPathPoint('SG',g,v3(A0)); s.updGeometryPath().appendNewPathPoint('GT',h,v3(Bs)); s.updGeometryPath().addPathWrap(w); m.addForce(s)
    st=m.initSystem(); co=m.getCoordinateSet().get('abd'); out=[]
    for e in range(121): co.setValue(st,np.radians(e)); m.realizePosition(st); out.append(s.getLength(st)*1000)
    return np.array(out)
osL=build(Bout); pyL=np.array([wrap(A0,rodr(k,np.radians(e))@Bout,Rw)*1000 for e in range(121)])
print('max |diff| %.2f mm, RMSE %.2f mm over 0-120 deg'%(np.abs(osL-pyL).max(),np.sqrt(((osL-pyL)**2).mean())))
