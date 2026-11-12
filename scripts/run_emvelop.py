"""Run public synthetic feasibility experiment; see docs/emvelop-usage.md."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import argparse,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.emvelop_feasibility import Config,run
p=argparse.ArgumentParser(); p.add_argument('--output',default='analysis/emvelop'); args=p.parse_args()
out=Path(args.output); out.mkdir(parents=True,exist_ok=True)
results=[]
for step in [.006,.004,.003]:
    result,points,e,ti=run(Config(),step); results.append(result)
(out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
fig,axes=plt.subplots(1,2,figsize=(10,4),layout='constrained')
mask=np.abs(points[:,2])<.001
for ax,value,title in zip(axes,[e,ti],['Same frequency: best phase','Different frequencies: envelope depth']):
    plot=ax.scatter(points[mask,0]*100,points[mask,1]*100,c=value[mask],s=9,cmap='inferno')
    ax.plot(0,3,'cx'); ax.set(xlabel='lateral x (cm)',ylabel='y (cm)',title=title,aspect='equal')
    fig.colorbar(plot,ax=ax,label='V/m')
fig.savefig(out/'fields.png',dpi=160); plt.close(fig)
print(json.dumps([{k:v for k,v in r.items() if k not in ('same_frequency_sweep','config')} for r in results],indent=2))
