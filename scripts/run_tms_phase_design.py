"""Extended bilateral loop study, see docs/tms-phase-report.md."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.tms_phase_design import search,evaluate,loop_nodes,loop_field,grid
out=Path('analysis/emvelop'); out.mkdir(exist_ok=True,parents=True)
rows,best=search(); converged=[]
for step in (.006,.004,.003):
    result,axis,plane,loops=evaluate(best,step); converged.append(result)
(out/'tms_extended.json').write_text(json.dumps(dict(observation_radius_m=.075,search_step_m=.006,target_m=[0,0,0],target_direction=[0,0,1],best=best,convergence=converged,candidates=rows),indent=2)+'\n')
fig,axs=plt.subplots(1,3,figsize=(14,4),layout='constrained')
ax=axs[0]
for loop in loops:
    node,_=loop_nodes(loop); ax.plot(node[:,0]*100,node[:,1]*100)
ax.add_patch(plt.Circle((0,0),7.5,fill=False,color='grey')); ax.plot(0,0,'rx'); ax.set(aspect='equal',xlabel='x (cm)',ylabel='y (cm)',title='Selected loops: top projection')
im=axs[1].pcolormesh(axis*100,axis*100,plane.T,shading='nearest',cmap='inferno')
axs[1].contour(axis*100,axis*100,plane.T,levels=[.5,1],colors=['cyan','white'])
axs[1].plot(0,0,'cx'); axs[1].set(aspect='equal',xlabel='x (cm)',ylabel='y (cm)',title='Peak E / target projection')
fig.colorbar(im,ax=axs[1],label='dimensionless')
axs[2].scatter([r['cube_root_half_target_volume_cm'] for r in rows],[r['target_at_5kA_each'] for r in rows],s=12,alpha=.5)
axs[2].plot(best['cube_root_half_target_volume_cm'],best['target_at_5kA_each'],'r*',ms=13)
axs[2].set(xlabel='Cube root half-target volume (cm)',ylabel='Target projection at 5 kA/coil (V/m)',title='Geometry / regularization candidates')
fig.savefig(out/'tms_extended.png',dpi=180)
points=grid(.003,.075)
w=np.array(best['weights_kA_real'])+1j*np.array(best['weights_kA_imag'])
field=sum(loop_field(points,l,segments=256)*weight for l,weight in zip(loops,w))
np.savez_compressed(out/'tms_extended_fields.npz',points=points,field=field,step=.003,radius=.075,target_projection=1.,sigma=.2,duty=.002)
print(json.dumps(dict(best=best,convergence=converged),indent=2))
