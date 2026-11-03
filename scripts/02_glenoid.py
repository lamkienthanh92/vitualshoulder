import trimesh, numpy as np, json
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
P='bp3d/assets/BodyParts3D_data/stl/'
L=lambda k: trimesh.load(P+k+'.stl', process=True)
sc,hu,cl,lh=L('FMA13395'),L('FMA23130'),L('FMA13322'),L('FMA37686')
Cr=np.load('work/C.npy'); C,R=Cr[:3],Cr[3]
print('verts',len(sc.vertices),len(hu.vertices),len(lh.vertices))

# ---- glenoid: scapula verts near head center, normals facing center
v=sc.vertices; n=sc.vertex_normals
d=np.linalg.norm(v-C,axis=1)
dirc=(C-v)/d[:,None]
facing=(n*dirc).sum(1)
mask=(d<R+14)&(d>R-6)&(facing>0.75)
g=v[mask]; gn=n[mask]
print('glenoid cand',len(g),'dist range',d[mask].min(),d[mask].max())
# keep biggest connected cluster via KD radius
tree=cKDTree(g)
lab=-np.ones(len(g),int); cur=0
for i in range(len(g)):
    if lab[i]>=0: continue
    stack=[i]; lab[i]=cur
    while stack:
        j=stack.pop()
        for k in tree.query_ball_point(g[j],3.0):
            if lab[k]<0: lab[k]=cur; stack.append(k)
    cur+=1
cnt=np.bincount(lab); big=cnt.argmax(); print('clusters',cnt[:8])
g=g[lab==big]; gn=gn[lab==big]
G=g.mean(0); N=gn.mean(0); N/=np.linalg.norm(N)
print('glenoid center',np.round(G,1),'normal(toward head)',np.round(N,2),'n',len(g))
# glenoid axes: superior axis = projection of +z on plane
up=np.array([0,0,1.]); su=up-(up@N)*N; su/=np.linalg.norm(su)
ap=np.cross(N,su); 
hh=(g-G)@su; ww=(g-G)@ap
print('glenoid height',hh.max()-hh.min(),'width',ww.max()-ww.min())
sup_pt=g[hh.argmax()]; inf_pt=g[hh.argmin()]
print('superior pole',np.round(sup_pt,1),'inferior pole',np.round(inf_pt,1))
np.savez('work/glen.npz',G=G,N=N,su=su,ap=ap,sup=sup_pt,inf=inf_pt,g=g)

# ---- other scapula landmarks
zmax=v[:,2].max()
acr=v[(v[:,2]>zmax-25)]
print('acromion lateral-most (min x among top25):',np.round(acr[acr[:,0].argmin()],1))
# coracoid tip: most anterior (min y) vertex among top 60 and lateral half
cand=v[(v[:,2]>zmax-60)]
cor=cand[cand[:,1].argmin()]
print('coracoid tip (min y):',np.round(cor,1))
