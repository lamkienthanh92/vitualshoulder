import json,numpy as np
rng=np.random.default_rng(2026)
C=json.load(open('curves.json')); L={k:np.array(v) for k,v in C.items()}
# ---- calibration constants from the literature
U_INT,U_TORN=3.0,6.4          # superior translation, mm (Mihata 2012)
DC=U_TORN-U_INT               # effect of the supraspinatus tear, mm
K=40/0.9                      # N/mm: deltoid 40->80 N raised the head 0.9 mm in torn shoulders (Singh 2019)
FC0=DC*K                      # effective cuff shear equivalent, N
def sd(th): return np.maximum(0.15,np.cos(np.radians(th)))
TH=np.arange(0,91)
def run(tech,fix,N=4000,seed=1):
    r=np.random.default_rng(seed)
    Fd=r.uniform(20,120,N); fc=r.uniform(-0.5,0.5,N); T0=r.uniform(0,40,N)
    dL=L[tech][:91]-L[tech][fix]                          # positive = taut
    dL0=L[tech][0]-L[tech][10] if tech not in('box','snake') else (L[tech][0]-L[tech][10])
    if tech=='fl':   k=(FC0-T0)/dL0                       # restores intact level at 0 deg when fixed at 10 deg (Mihata 2017)
    elif tech=='hda':k=(0.5*FC0-T0)/dL0                   # restores about half
    else:            k=r.uniform(10,40,N)                 # no biomechanical data: broad prior
    Fg=np.maximum(0,T0[:,None]+k[:,None]*dL[None,:])      # N, graft force vs abduction
    du=(FC0*(1-fc)[:,None]-Fg+(Fd-40)[:,None]*sd(TH)[None,:])/K   # excess translation vs intact, mm
    return dict(Fd=Fd,fc=fc,T0=T0,k=k,Fg=Fg,du=du)
def src(X,y):
    Z=(X-X.mean(0))/X.std(0); yy=(y-y.mean())/y.std(); b=np.linalg.lstsq(Z,yy,rcond=None)[0]; r2=1-((yy-Z@b)**2).sum()/(yy**2).sum(); return b,r2
print('Calibration: tear effect %.1f mm, K=%.0f N/mm, cuff shear equivalent %.0f N'%(DC,K,FC0))
print('\n== Untreated SSP tear (no graft), excess translation vs intact, median [5-95%] (mm), F_d 20-120 N, cuff residual -0.5..0.5')
r=run('fl',30); du0=(FC0*(1-r['fc'])[:,None]+(r['Fd']-40)[:,None]*sd(TH)[None,:])/K
print('  0deg %.1f [%.1f,%.1f]  30deg %.1f [%.1f,%.1f]  60deg %.1f [%.1f,%.1f]'%tuple(v for t in (0,30,60) for v in (np.median(du0[:,t]),np.percentile(du0[:,t],5),np.percentile(du0[:,t],95))))
print('\n== With graft: excess translation vs intact (mm) and peak graft force (N), median [5-95%]')
print('%-8s %-4s | %-20s %-20s %-20s | %-18s'%('tech','fix','du 0deg','du 30deg','du 60deg','peak force N'))
res={}
for tech in ['fl','hda','lhbt','chinese','loop','box','snake']:
    for fix in (10,30,45):
        r=run(tech,fix); res[(tech,fix)]=r
        f=lambda t:'%.1f [%.1f,%.1f]'%(np.median(r['du'][:,t]),np.percentile(r['du'][:,t],5),np.percentile(r['du'][:,t],95))
        pk=r['Fg'].max(1)
        print('%-8s %-4d | %-20s %-20s %-20s | %.0f [%.0f,%.0f]'%(tech,fix,f(0),f(30),f(60),np.median(pk),np.percentile(pk,5),np.percentile(pk,95)))
print('\n== Which inputs drive the result? standardised regression coefficients (|SRC|, R2) for du at 30 deg')
for tech,fix in [('fl',30),('hda',30),('lhbt',30),('lhbt',10)]:
    r=res[(tech,fix)]; X=np.column_stack([r['Fd'],r['fc'],r['T0'],r['k']]); names=['deltoid F_d','cuff residual','initial tension','graft stiffness']
    b,r2=src(X,r['du'][:,30]); print('  %-6s fix %2d: '%(tech,fix)+', '.join('%s %+.2f'%(n,x) for n,x in zip(names,b))+'  (R2=%.2f)'%r2)
print('\n== and for peak graft force')
for tech,fix in [('fl',30),('lhbt',30)]:
    r=res[(tech,fix)]; X=np.column_stack([r['Fd'],r['fc'],r['T0'],r['k']]); b,r2=src(X,r['Fg'].max(1)); print('  %-6s fix %2d: '%(tech,fix)+', '.join('%s %+.2f'%(n,x) for n,x in zip(['deltoid F_d','cuff residual','initial tension','graft stiffness'],b))+'  (R2=%.2f)'%r2)
# deltoid-load effect at 30 deg for lhbt fix 30
r=res[('lhbt',30)]; 
for lo,hi in [(20,50),(50,80),(80,120)]:
    m=(r['Fd']>=lo)&(r['Fd']<hi); print('  LHBT fix30, deltoid %d-%d N: du30 median %.2f mm'%(lo,hi,np.median(r['du'][m,30])))

# ---- save the summary table
import csv
with open('pilot_results.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['technique','fixation_deg','du0_median_mm','du0_p5','du0_p95','du30_median_mm','du30_p5','du30_p95','du60_median_mm','du60_p5','du60_p95','peak_graft_force_median_N','peak_p5','peak_p95'])
    for (tech,fix),r in res.items():
        row=[tech,fix]
        for t in (0,30,60): row+= [round(float(np.median(r['du'][:,t])),2),round(float(np.percentile(r['du'][:,t],5)),2),round(float(np.percentile(r['du'][:,t],95)),2)]
        pk=r['Fg'].max(1); row+=[round(float(np.median(pk))),round(float(np.percentile(pk,5))),round(float(np.percentile(pk,95)))]
        w.writerow(row)
