import trimesh, numpy as np, json, base64, fast_simplification
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
P='bp3d/assets/BodyParts3D_data/stl/'
def L(k):
    m=trimesh.load(P+k+'.stl',process=True)
    parts=m.split(only_watertight=False)
    return max(parts,key=lambda p:len(p.faces))
Cr=np.load('work/C.npy'); C,R=Cr[:3],Cr[3]
def F(p):  # LPS -> three frame, origin at head center (x subject-left, y up, z anterior)
    p=np.asarray(p,float)-C
    return np.stack([p[...,0],p[...,2],-p[...,1]],-1)
def LM_(ks):
    ms=[L(k) for k in ks]; return ms
raw={'scap':L('FMA13395'),'hum':L('FMA23130'),'clav':L('FMA13322'),
     'ssp':L('FMA32544'),'isp':L('FMA32547'),'ssc':L('FMA13414'),'tm':L('FMA32553'),'lhb':L('FMA37686'),'tmaj':L('FMA32551'),'cbr':L('FMA37665'),'sh':L('FMA37684'),'tlh':L('FMA37699')}
delt_parts=[L('FMA34680'),L('FMA34682'),L('FMA34684')]
# ---- bone sample clouds (original frame) for skinning weights
raw['delt']=trimesh.util.concatenate(delt_parts)
Cpts=trimesh.sample.sample_surface(raw['clav'],60000)[0]
tc=cKDTree(Cpts)
Spts=trimesh.sample.sample_surface(raw['scap'],200000)[0]
Hpts=trimesh.sample.sample_surface(raw['hum'],150000)[0]
ts,th=cKDTree(Spts),cKDTree(Hpts)

# ---- LHB centerline via geodesic bins (original frame)
gl=np.load('work/glen.npz'); sup=gl['sup']
lh=raw['lhb']; v=lh.vertices
tip=np.linalg.norm(v-sup,axis=1).argmin()
e=lh.edges_unique; w=np.linalg.norm(v[e[:,0]]-v[e[:,1]],axis=1)
A=coo_matrix((np.r_[w,w],(np.r_[e[:,0],e[:,1]],np.r_[e[:,1],e[:,0]])),shape=(len(v),)*2).tocsr()
geo=dijkstra(A,indices=tip)
step=2.0; cl=[]
for s in np.arange(0,125,step):
    m=(geo>=s)&(geo<s+step)
    if m.sum()<5: continue
    cl.append(np.r_[s+step/2, v[m].mean(0)])
cl=np.array(cl)
# smooth the centerline (3-pt moving average, endpoints kept)
sm=cl.copy()
for i in range(1,len(cl)-1): sm[i,1:]=(cl[i-1,1:]+cl[i,1:]+cl[i+1,1:])/3
cl=sm
def at(s): 
    i=np.abs(cl[:,0]-s).argmin(); return cl[i,1:]
A_pt=cl[0,1:]; 
S_ENTRY,S_END=56.0,110.0
B_pt=at(S_ENTRY)
groove=cl[(cl[:,0]>=S_ENTRY)&(cl[:,0]<=S_END),1:]
print('groove pts',len(groove),'A',np.round(A_pt,1),'B',np.round(B_pt,1))

# ---- decimate helper
def deci(m,target,keep_mask_faces=None):
    vv,ff=m.vertices.copy(),m.faces.copy()
    if keep_mask_faces is not None: ff=ff[keep_mask_faces]
    # compact
    used=np.unique(ff); remap=-np.ones(len(vv),int); remap[used]=np.arange(len(used))
    vv=vv[used]; ff=remap[ff]
    if len(ff)>target:
        vv,ff=fast_simplification.simplify(vv.astype(np.float32),ff.astype(np.int32),target_reduction=1-target/len(ff),agg=5)
    return np.asarray(vv,float),np.asarray(ff,np.int32)

targets={'scap':22000,'hum':13000,'clav':3500,'ssp':6000,'isp':9000,'ssc':9000,'tm':5000,'lhb':6000,'delt':9000,'tmaj':4000,'cbr':3000,'sh':5000,'tlh':5000}
meshes={}
for k,m in raw.items():
    if k=='lhb':
        # keep the belly only: faces whose 3 vertices have geodesic >= 104 from tip
        g=geo[m.faces]; keepf=(g.min(1)>=104)&np.isfinite(g).all(1)
        vv,ff=deci(m,targets[k],keepf)
    else:
        vv,ff=deci(m,targets[k])
    wt=None; wc=None
    if k in ('ssp','isp','ssc','tm'):
        ds,_=ts.query(vv); dh,_=th.query(vv)
        wt=ds/(ds+dh+1e-6); wt=wt*wt*(3-2*wt); wc=np.zeros(len(vv))
    if k in ('delt','tmaj','cbr','sh','tlh'):
        ds,_=ts.query(vv); dh,_=th.query(vv); dc,_=tc.query(vv)
        a=1/(ds+1.5)**3; b=1/(dc+1.5)**3; c=1/(dh+1.5)**3; z=a+b+c
        wt=c/z; wc=b/z
    if k=='lhb': wt=np.ones(len(vv)); wc=np.zeros(len(vv))
    meshes[k]=(F(vv).astype(np.float32),ff.astype(np.uint16),wt,wc)
    print(k,'verts',len(vv),'faces',len(ff),'' if wt is None else 'w mean %.2f  frac<0.1 %.2f frac>0.9 %.2f'%(wt.mean(),(wt<0.1).mean(),(wt>0.9).mean()))

# ---- landmarks (three frame)
LM={}
vs=raw['scap'].vertices; zmax=vs[:,2].max()
top=vs[vs[:,2]>zmax-25]
LM['acromion']=F(top[top[:,0].argmin()])
cand=vs[vs[:,2]>zmax-60]; LM['coracoid']=F(cand[cand[:,1].argmin()])
LM['glenoid']=F(gl['G']); LM['supraglenoid']=F(gl['sup']); LM['infraglenoid']=F(gl['inf'])
LM['inferiorAngle']=F(vs[vs[:,2].argmin()])
vc=raw['clav'].vertices
lat=vc[vc[:,0].argmin()]; med=vc[vc[:,0].argmax()]
LM['clavLat']=F(vc[np.linalg.norm(vc-lat,axis=1)<6].mean(0)); LM['clavMed']=F(med)
LM['groove']=F(at(80.0))
LM['entry']=F(B_pt); LM['tendonStart']=F(A_pt)
# footprints on humerus
fp={}
for k in ('ssp','isp','ssc','tm'):
    mv=raw[k].vertices; dh,_=th.query(mv); fp[k]=F(mv[dh<2.5].mean(0))
LM['gt']=fp['ssp']; LM['lt']=fp['ssc']
# shaft / epicondyle
hv=raw['hum'].vertices; zmin=hv[:,2].min(); E=hv[hv[:,2]<zmin+30].mean(0)
LM['epicondyleMid']=F(E)
# scapular plane normal (body of scapula), pivot AC
body=vs[vs[:,2]<zmax-70]; Q=body-body.mean(0)
wv,VV=np.linalg.eigh(Q.T@Q/len(Q)); nrm=VV[:,0]  # least variance
nrm3=np.array([nrm[0],nrm[2],-nrm[1]])
gn=F(gl['G']+gl['N'])-F(gl['G'])   # glenoid normal (toward head) in three frame
gn/=np.linalg.norm(gn)
# sign so that +theta about axis raises glenoid normal's Y (upward rotation)
def rot(axis,ang,vec):
    k=axis/np.linalg.norm(axis); c,s=np.cos(ang),np.sin(ang)
    return vec*c+np.cross(k,vec)*s+k*(k@vec)*(1-c)
for sgn in (1,-1):
    r=rot(sgn*nrm3,np.radians(10),gn); print('sgn',sgn,'normal y',round(gn[1],3),'->',round(r[1],3))
sgn=1 if rot(nrm3,np.radians(10),gn)[1]>gn[1] else -1
axisST=sgn*nrm3
print('scapular plane normal (three)',np.round(axisST,3),'glenoid normal',np.round(gn,3))
LM['stAxis']=axisST; LM['pivotAC']=LM['clavLat']
LM['glenoidNormal']=gn
print({k:np.round(v,1).tolist() for k,v in LM.items()})

# ---- pack
blob=bytearray(); man={}
def pad(): 
    while len(blob)%4: blob.append(0)
for k,(vv,ff,wt,wc) in meshes.items():
    mn=vv.min(0); mx=vv.max(0); sc=(mx-mn)/65535.0
    q=np.round((vv-mn)/sc).astype(np.uint16)
    pad(); op=len(blob); blob+=q.tobytes()
    pad(); oi=len(blob); blob+=ff.astype(np.uint16).tobytes()
    ow=-1
    if wt is not None:
        pad(); ow=len(blob); blob+=np.round(np.clip(wt,0,1)*255).astype(np.uint8).tobytes()
    oc=-1
    if wc is not None:
        pad(); oc=len(blob); blob+=np.round(np.clip(wc,0,1)*255).astype(np.uint8).tobytes()
    man[k]={'n':len(vv),'m':len(ff),'min':mn.round(4).tolist(),'sc':sc.tolist(),'op':op,'oi':oi,'ow':ow,'oc':oc}
pad()
data={'man':man,'lm':{k:np.round(v,2).tolist() for k,v in LM.items()},
      'groove':np.round(F(groove),2).tolist(),'Rhead':round(float(R),2),'Rwrap':25.8}
json.dump(data,open('work/data.json','w'))
open('work/blob.b64','w').write(base64.b64encode(bytes(blob)).decode())
print('blob bytes',len(blob),'b64',len(base64.b64encode(bytes(blob))))
np.savez('work/decimated.npz',**{k:v[0] for k,v in meshes.items()},**{k+'_f':v[1] for k,v in meshes.items()})
