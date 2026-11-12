"""Independent optimization-grid refinement; preserve main experiment artifacts."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from src.emvelop_rf import RFConfig,sources,transfer,grid,optimize,evaluate
c=RFConfig(); ss=sources(c); target=[transfer(np.zeros((1,3)),s,c)[0] for s in ss]
p,mask,axis=grid(.004,c);p=p[np.linalg.norm(p,axis=1)>1e-10]
g=[transfer(p,s,c) for s in ss]
initial,final,trials,fun=optimize(*g,*target,seeds=3)
p,mask,axis=grid(.003,c);g=[transfer(p,s,c) for s in ss]
summary={'optimization_grid_m':.004,'evaluation_grid_m':.003,'trials':trials,
 'MFT':evaluate(g,final,.003,mask,c)[0],
 'weights':[{'real':w.real.tolist(),'imag':w.imag.tolist()} for w in final]}
old=json.load(open('analysis/emvelop/rf_results.json'))
summary['six_mm_optimization_evaluated_at_3mm']=old['evaluations'][-1]['MFT']
Path('analysis/emvelop/rf_refinement.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='weights'},indent=2))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,axes=plt.subplots(1,3,figsize=(12,3.7),layout='constrained')
for label,values in [('6 mm optimization',old['trials']),('4 mm optimization',trials)]:
    axes[0].plot([v['seed'] for v in values],[v['objective'] for v in values],'o-',label=label)
a=summary['six_mm_optimization_evaluated_at_3mm']; b=summary['MFT']
axes[0].set(xlabel='Initialization index',ylabel='Mean off-target minimum carrier power',title='Local solver sensitivity');axes[0].legend(fontsize=8)
axes[1].bar(['6 mm','4 mm'],[a['cube_root_half_target_volume_cm'],b['cube_root_half_target_volume_cm']]);axes[1].set(ylabel='Cube root half-target volume (cm)',xlabel='Optimization grid',title='Both evaluated at 3 mm')
axes[2].bar(['6 mm','4 mm'],[a['target_at_cube_average_10Wkg_V_m'],b['target_at_cube_average_10Wkg_V_m']]);axes[2].set(ylabel='Target envelope at same SAR proxy (V/m)',xlabel='Optimization grid',title='Both evaluated at 3 mm')
fig.savefig('analysis/emvelop/rf_refinement.png',dpi=170)
