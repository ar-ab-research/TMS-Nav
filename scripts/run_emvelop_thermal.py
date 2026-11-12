"""Apply identical steady bioheat assumptions to saved RF and TMS fields."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.emvelop_thermal import steady_temperature
out=Path('analysis/emvelop'); rf=np.load(out/'rf_fields.npz'); tms=np.load(out/'tms_extended_fields.npz')
cases=[]
for name in ['MIT_like','MFT']:
 q=.5*(np.sum(abs(rf[name+'_E1'])**2,axis=1)+np.sum(abs(rf[name+'_E2'])**2,axis=1))
 m=2*np.minimum(np.linalg.norm(rf[name+'_E1'],axis=1),np.linalg.norm(rf[name+'_E2'],axis=1))
 cases.append((name,rf['points'],float(rf['step']),q,m))
f=tms['field']; a=np.sum(abs(f)**2,axis=1); b=abs(np.sum(f*f,axis=1)); peak=np.sqrt((a+b)/2)
q=.5*.2*.002*a
cases.append(('TMS',tms['points'],float(tms['step']),q,peak))
results=[]; fig,axes=plt.subplots(2,3,figsize=(13,8),layout='constrained')
for col,(name,points,step,q,field) in enumerate(cases):
 temp,qc=steady_temperature(points,q,step)
 alpha=1/np.sqrt(temp.max()); center=np.argmin(np.linalg.norm(points,axis=1)); target=field[center]
 l50=(np.count_nonzero(field>=.5*target)*step**3)**(1/3)*100
 row=dict(name=name,target_unscaled_V_m=float(target),max_deltaT_unscaled_K=float(temp.max()),scale_to_1K=float(alpha),target_at_1K_V_m=float(alpha*target),cube_root_half_volume_cm=float(l50),max_pointwise_sar_at_1K_W_kg=float(q.max()*alpha**2/1000),**qc)
 results.append(row)
 mask=abs(points[:,2])<step*.1
 for r,val,label in [(0,field*alpha,'Field at 1 K ceiling (V/m)'),(1,temp*alpha**2,'Temperature rise (K)')]:
  ax=axes[r,col]; im=ax.scatter(points[mask,0]*100,points[mask,1]*100,c=val[mask],s=10,cmap='inferno'); ax.plot(0,0,'cx'); ax.set(title=name,xlabel='x (cm)',ylabel='y (cm)',aspect='equal'); fig.colorbar(im,ax=ax,label=label)
fig.savefig(out/'thermal_comparison.png',dpi=160); plt.close(fig)
(out/'thermal_comparison.json').write_text(json.dumps(dict(assumptions=dict(thermal_conductivity_W_m_K=.5,perfusion_sink_W_m3_K=10000,rho_kg_m3=1000,RF_sigma_S_m=1,TMS_sigma_S_m=.2,TMS_duty=.002,outer_boundary='insulating',temperature_ceiling_K=1),results=results),indent=2)+'\n')
print(json.dumps(results,indent=2))
