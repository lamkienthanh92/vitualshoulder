import trimesh, numpy as np, json
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
P='bp3d/assets/BodyParts3D_data/stl/'
L=lambda k: trimesh.load(P+k+'.stl', process=False)
sc,hu,cl,lh=L('FMA13395'),L('FMA23130'),L('FMA13322'),L('FMA37686')

# ---- humeral head sphere fit (proximal vertices)
v=hu.vertices; ztop=v[:,2].max()
prox=v[v[:,2]>ztop-45]
def fit_sphere(pts,r0=24):
    c0=pts.mean(0)
    f=lambda p: np.linalg.norm(pts-p[:3],axis=1)-p[3]
    r=least_squares(f,np.r_[c0,r0],loss='soft_l1',f_scale=1.5)
    return r.x
# iterate: keep points near sphere
pts=prox
for i in range(6):
    s=fit_sphere(pts); c,R=s[:3],s[3]
    d=np.abs(np.linalg.norm(prox-c,axis=1)-R)
    pts=prox[d<2.0]
    print(i,np.round(c,1),round(R,1),len(pts))
C,R=c,R
art=hu.vertices[np.abs(np.linalg.norm(hu.vertices-C,axis=1)-R)<1.5]
print('articular verts',len(art),'center',art.mean(0))
np.save('work/C.npy',np.r_[C,R])
