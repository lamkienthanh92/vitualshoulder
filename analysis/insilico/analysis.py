# Cadaver workbook: place giai_phau_bo_sung.xlsx next to this script (not included; the per-shoulder values are also in index.html, CAD.rows).
import json,itertools,numpy as np,openpyxl,csv
from scipy import stats
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'serif','font.size':10,'axes.linewidth':0.8,'hatch.linewidth':0.8})
# ------------------------------------------------------------------ 1. variability of the required graft path (4 CT shoulders + template)
V=json.load(open('variab.json')); techs=['lhbt','chinese','loop','box','snake']
names={'lhbt':'LHBT in situ','chinese':'Chinese way','loop':'Biceps loop','box':'Box (2 bundles)','snake':'Snake (2 bundles)'}
cases={'001':'L','002':'L','003':'R','004':'L'}
rows=[]
for t in techs:
    for c in ['tpl','001','002','003','004']:
        a=V[('tpl_' if c=='tpl' else c+'_')+t]
        rows.append([t,'template' if c=='tpl' else 'case '+c,'' if c=='tpl' else cases[c],round(a[0],1),round(a[1],1),round(a[2],1),round(a[0]-a[1],1),round(a[1]-a[2],1)])
with open('variability_by_case.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['technique','shoulder','side','path_0deg_mm','path_30deg_mm_(fixation)','path_60deg_mm','taut_at_0deg_vs_30deg_mm','slack_at_60deg_vs_30deg_mm']); w.writerows(rows)
fig,ax=plt.subplots(figsize=(7.2,3.6)); hat=['','///','\\\\\\','xxx','...']; lab=['Template','Case 001','Case 002','Case 003','Case 004']; wd=0.16
for i,c in enumerate(['tpl','001','002','003','004']):
    y=[V[('tpl_' if c=='tpl' else c+'_')+t][1] for t in techs]
    ax.bar(np.arange(len(techs))+(i-2)*wd,y,wd,color='white' if i else '#d9d9d9',edgecolor='black',hatch=hat[i],label=lab[i],linewidth=0.8)
ax.set_xticks(range(len(techs))); ax.set_xticklabels([names[t] for t in techs],fontsize=8.5); ax.set_ylabel('Graft path length at fixation (30°), mm'); ax.legend(frameon=False,fontsize=8,ncol=5,loc='upper left',bbox_to_anchor=(0,1.12)); ax.spines[['top','right']].set_visible(False)
plt.tight_layout(); plt.savefig('fig1_required_path_length.png',dpi=300); plt.savefig('fig1_required_path_length.pdf'); plt.close()
spread={t:(min(V[k+'_'+t][1] for k in cases),max(V[k+'_'+t][1] for k in cases),np.std([V[k+'_'+t][1] for k in cases],ddof=1)/np.mean([V[k+'_'+t][1] for k in cases])*100) for t in techs}
# ------------------------------------------------------------------ 2. cadaver tendon dimensions
ws=openpyxl.load_workbook('giai_phau_bo_sung.xlsx',data_only=True).active
hdr=[c.value for c in ws[1]][3:13]; get=lambda r:[ws.cell(row=r,column=c).value for c in range(4,14)]
thick,width,capA,capP=None,None,None,None
for r in range(1,ws.max_row+1):
    k=ws.cell(row=r,column=3).value
    if k=='chiều dày nhị đầu':thick=np.array(get(r),float)
    if k=='chiều rộng nhị đầu':width=np.array(get(r),float)
    if k=='chiều dày bao khớp trên trước':capA=np.array(get(r),float)
    if k=='chiều dày bao khớp trên sau':capP=np.array(get(r),float)
side=np.array(['R' if 'phải' in h else 'L' for h in hdr]); cad=np.array([h.split()[0] for h in hdr])
def ms(x): return '%.1f ± %.1f (median %.1f, range %.1f–%.1f)'%(x.mean(),x.std(ddof=1),np.median(x),x.min(),x.max())
print('n shoulders',len(width),'cadavers',len(set(cad)))
print('LHB width  :',ms(width)); print('LHB thick. :',ms(thick)); print('cap. ant.  :',ms(capA)); print('cap. post. :',ms(capP))
narrow=width<5; k=int(narrow.sum()); n=len(width)
cp=stats.beta.ppf([0.025,0.975],[k,k+1],[n-k+1,n-k]); cp[0]=stats.beta.ppf(0.025,k,n-k+1); cp[1]=stats.beta.ppf(0.975,k+1,n-k)
print('width <5 mm (Snake contraindication, Kim 2019): %d/%d = %.0f%%, exact 95%% CI %.0f–%.0f%%'%(k,n,100*k/n,100*cp[0],100*cp[1]))
print('  by cadaver (R,L widths):',{c:(width[(cad==c)&(side=="R")][0],width[(cad==c)&(side=="L")][0]) for c in sorted(set(cad))})
print('  cadavers with both sides <5 mm:',sum(1 for c in set(cad) if (width[cad==c]<5).all()),'; one side only:',sum(1 for c in set(cad) if 0<(width[cad==c]<5).sum()<2))
Rw=np.array([width[(cad==c)&(side=="R")][0] for c in sorted(set(cad))]); Lw=np.array([width[(cad==c)&(side=="L")][0] for c in sorted(set(cad))])
# exact permutation test for the Spearman correlation between right and left widths (5 pairs)
rho=stats.spearmanr(Rw,Lw)[0]; perms=[stats.spearmanr(Rw,np.array(p))[0] for p in itertools.permutations(Lw)]; p_exact=np.mean([abs(x)>=abs(rho)-1e-12 for x in perms])
print('  right vs left width across cadavers: Spearman rho = %.2f, exact two-sided p = %.4f (n=5 pairs)'%(rho,p_exact))
w=stats.wilcoxon(Rw,Lw,method='exact'); print('  right vs left width, exact Wilcoxon signed-rank p = %.4f'%w.pvalue)
rA=thick/capA; rP=thick/capP
print('LHB thickness / anterior capsule: median %.1f (range %.1f–%.1f);  / posterior capsule: median %.1f (range %.1f–%.1f)'%(np.median(rA),rA.min(),rA.max(),np.median(rP),rP.min(),rP.max()))
for th in (3.4,6,8): print('  graft %.1f mm / capsule: anterior %.1f–%.1f×, posterior %.1f–%.1f×'%(th,(th/capA).min(),(th/capA).max(),(th/capP).min(),(th/capP).max()))
area=np.pi/4*width*thick; print('LHB cross-section (ellipse) mm²: ',ms(area))
cor=stats.spearmanr(width,capA); print('width vs anterior capsule thickness: Spearman rho %.2f, p=%.4f (n=10 shoulders, clustered by cadaver)'%cor)
with open('tendon_eligibility.csv','w',newline='') as f:
    w_=csv.writer(f); w_.writerow(['cadaver','side','lhb_width_mm','lhb_thickness_mm','cap_ant_mm','cap_post_mm','lhb_thick_over_cap_ant','lhb_thick_over_cap_post','ellipse_area_mm2','snake_width_ge_5mm'])
    for i in range(n): w_.writerow([cad[i],side[i],width[i],thick[i],capA[i],capP[i],round(rA[i],2),round(rP[i],2),round(area[i],1),'yes' if width[i]>=5 else 'no'])
fig,axs=plt.subplots(1,2,figsize=(7.2,3.2)); x=np.arange(n)
for ax,y,lab_,ref in ((axs[0],width,'LHB width, mm',5),(axs[1],thick,'LHB thickness, mm',None)):
    ax.bar(x,y,0.7,color=['white' if s=='R' else '#bdbdbd' for s in side],edgecolor='black',hatch=None,linewidth=0.8)
    for i,s in enumerate(side):
        if s=='L': ax.patches[i].set_hatch('///')
    if ref: ax.axhline(ref,color='black',ls='--',lw=0.9)
    ax.set_xticks(x); ax.set_xticklabels([c+s for c,s in zip(cad,side)],rotation=60,fontsize=7.5); ax.set_ylabel(lab_); ax.spines[['top','right']].set_visible(False)
axs[0].bar([0],[0],color='white',edgecolor='black',label='Right'); axs[0].bar([0],[0],color='#bdbdbd',edgecolor='black',hatch='///',label='Left'); axs[0].legend(frameon=False,fontsize=8,loc='upper right')
plt.tight_layout(); plt.savefig('fig2_lhb_width_thickness.png',dpi=300); plt.savefig('fig2_lhb_width_thickness.pdf'); plt.close()
print('\nVariability of required path at 30°, four CT shoulders (min–max, CV):'); [print('  %-18s %.1f–%.1f mm, CV %.0f%%'%(names[t],*spread[t]) ) for t in techs]
