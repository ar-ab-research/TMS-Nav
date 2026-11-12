"""Run RF method reconstruction without fitting published outcome values."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import json
from dataclasses import asdict
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.emvelop_rf import RFConfig,sources,transfer,grid,optimize,evaluate
out=Path('analysis/emvelop'); out.mkdir(exist_ok=True,parents=True)
c=RFConfig(); ss=sources(c); target=[transfer(np.zeros((1,3)),s,c)[0] for s in ss]
p,mask,axis=grid(.006,c); p=p[np.linalg.norm(p,axis=1)>1e-10]
g=[transfer(p,s,c) for s in ss]
initial,final,trials,_=optimize(*g,*target)
weights={'MIT_like':initial,'MFT':final}
summary={'config':asdict(c),'optimization_grid_m':.006,'trials':trials,'evaluations':[],'weights':{}}
for name,ww in weights.items():
    summary['weights'][name]=[dict(real=w.real.tolist(),imag=w.imag.tolist(),amplitude_A=abs(w).tolist(),phase_deg=np.angle(w,deg=True).tolist(),target_residual=float(np.linalg.norm(t@w-[0,0,.5]))) for t,w in zip(target,ww)]
for step in [.006,.004,.003]:
    p,mask,axis=grid(step,c); g=[transfer(p,s,c) for s in ss]
    item={'grid_step_m':step,'voxel_count':len(p)}
    for name,ww in weights.items(): item[name]=evaluate(g,ww,step,mask,c)[0]
    summary['evaluations'].append(item)
(out/'rf_results.json').write_text(json.dumps(summary,indent=2)+'\n')
np.savez_compressed(out/'rf_fields.npz',points=p,step=.003,mask=mask,axis=axis,
 **{name+'_E'+str(i+1):np.einsum('ncm,m->nc',g[i],w[i]) for name,w in weights.items() for i in range(2)})
fig,axes=plt.subplots(2,3,figsize=(13,7),layout='constrained')
plane=abs(p[:,2])<1e-8
for row,(name,ww) in enumerate(weights.items()):
    info,envelope,sar=evaluate(g,ww,.003,mask,c)
    scale=info['target_at_cube_average_10Wkg_V_m']
    for col,(value,title) in enumerate([(envelope*scale,'Envelope proxy (V/m)'),(sar*scale**2,'Pointwise SAR (W/kg)')]):
        ax=axes[row,col]; sc=ax.scatter(p[plane,0]*100,p[plane,1]*100,c=value[plane],s=8,cmap='magma')
        ax.plot(0,0,'c+'); ax.set(title=name+': '+title,xlabel='x (cm)',ylabel='y (cm)',aspect='equal');fig.colorbar(sc,ax=ax)
    ax=axes[row,2]
    for i,w in enumerate(ww):ax.plot(np.arange(12),np.angle(w,deg=True),'o-',label='Array '+str(i+1))
    ax.set(title=name+': excitation phase',xlabel='Element index',ylabel='degrees');ax.legend()
fig.savefig(out/'rf_fields.png',dpi=170);plt.close(fig)
fig,axes=plt.subplots(1,2,figsize=(10,4),layout='constrained')
for name,ww in weights.items():
    info=summary['evaluations'][-1][name]
    axes[0].scatter(info['cube_root_half_target_volume_cm'],info['target_at_cube_average_10Wkg_V_m'],label='Synthetic '+name,s=70)
    axes[1].plot(abs(ww[0]),'o-',label=name+' array 1')
axes[0].scatter([3.59,2.78],[11.98,3.04],marker='x',s=80,label='Published anatomical results')
axes[0].set(xlabel='Cube root half-target volume (cm)',ylabel='Target envelope (V/m)',title='Different models: no numerical reproduction claim')
axes[1].set(xlabel='Element index',ylabel='Current (A), unit target envelope',title='Optimized amplitude distribution')
for ax in axes:ax.legend(fontsize=8)
fig.savefig(out/'rf_tradeoff.png',dpi=170);plt.close(fig)
print(json.dumps({'trials':trials,'finest':summary['evaluations'][-1]},indent=2))
