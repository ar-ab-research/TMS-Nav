"""Vacuum primary-field loop model; homogeneous heating is postprocessing only.

SI units, peak sinusoidal phasors. No tissue boundary charges or neural model.
"""
from dataclasses import dataclass, asdict
import numpy as np

@dataclass
class Config:
    head_radius: float = .09
    coil_x: float = .10
    coil_radius: float = .05
    frequency: float = 3000.
    peak_current: float = 5000.
    conductivity: float = .2
    density: float = 1000.
    duty: float = .002  # 200 us sinusoidal-equivalent burst x 10 Hz
    sar_budget: float = 2.  # illustrative pointwise average W/kg; not compliance
    target_y: float = .03
    segments: int = 256


def loop_a(points, x, radius, segments=256):
    """A/I = mu0/(4pi) integral dl/r for loop in yz plane, +x normal."""
    p = np.asarray(points, dtype=float)
    theta = (np.arange(segments)+.5)*2*np.pi/segments
    source = np.column_stack((np.full(segments,x),radius*np.cos(theta),radius*np.sin(theta)))
    dl = np.column_stack((np.zeros(segments),-radius*np.sin(theta),radius*np.cos(theta)))*2*np.pi/segments
    result = np.empty_like(p)
    for start in range(0,len(p),1024):
        distance = np.linalg.norm(p[start:start+1024,None,:]-source[None,:,:],axis=2)
        if np.any(distance < 1e-12):
            raise ValueError('Observation point lies on filament')
        result[start:start+1024] = 1e-7*np.einsum('ps,sk->pk',1/distance,dl)
    return result


def fields(points,c):
    # Common -i factor does not affect norm or relative phase.
    return tuple(2*np.pi*c.frequency*c.peak_current*loop_a(points,x,c.coil_radius,c.segments) for x in (-c.coil_x,c.coil_x))


def magnitude(a,b,phase):
    return np.linalg.norm(a+np.exp(1j*phase)*b,axis=-1)


def sar(peak_field,c,duty=None):
    return c.conductivity*np.asarray(peak_field)**2*(c.duty if duty is None else duty)/(2*c.density)


def grid(step,radius):
    axis=np.arange(-radius,radius+step*.1,step)
    xyz=np.stack(np.meshgrid(axis,axis,axis,indexing='ij'),axis=-1).reshape(-1,3)
    return xyz[np.linalg.norm(xyz,axis=1)<=radius+1e-10]


def run(c,step=.005):
    points=grid(step,c.head_radius)
    a,b=fields(points,c)
    ta,tb=fields(np.array([[0,c.target_y,0]]),c)
    rows=[]
    # Minimize suprathreshold volume at fixed target amplitude; reject null target.
    for degrees in range(181):
        phase=np.deg2rad(degrees)
        target=float(magnitude(ta,tb,phase)[0])
        if target < 1e-6: continue
        e=magnitude(a,b,phase)
        volume=float(np.count_nonzero(e>=.5*target)*step**3)
        maxsar=float(np.max(sar(e,c)))
        rows.append(dict(phase_deg=degrees,target_V_m=target,half_target_volume_cm3=volume*1e6,
            equivalent_sphere_diameter_cm=2*(3*volume/(4*np.pi))**(1/3)*100,
            target_to_max=float(target/e.max()),max_sar_W_kg=maxsar,
            target_at_sar_budget_V_m=float(target*np.sqrt(c.sar_budget/maxsar))))
    best=min(rows,key=lambda r:(r['half_target_volume_cm3'],-r['target_to_max']))
    phase=np.deg2rad(best['phase_deg']); e=magnitude(a,b,phase)
    # For coaxial loops fields are parallel everywhere: exact vector envelope depth.
    ti=2*np.minimum(np.linalg.norm(a,axis=1),np.linalg.norm(b,axis=1))
    ti_target=float(2*min(np.linalg.norm(ta),np.linalg.norm(tb)))
    ti_sar=c.conductivity*(np.sum(a*a,axis=1)+np.sum(b*b,axis=1))/(2*c.density)
    vol=float(np.count_nonzero(ti>=.5*ti_target)*step**3)
    # Evaluate paper-like sqrt(area) independently on an exact z=0 plane.
    axis=np.arange(-c.head_radius,c.head_radius+step*.1,step)
    xy=np.stack(np.meshgrid(axis,axis,indexing='ij'),axis=-1).reshape(-1,2)
    xy=xy[np.linalg.norm(xy,axis=1)<=c.head_radius+1e-10]
    plane=np.column_stack((xy,np.zeros(len(xy))))
    pa,pb=fields(plane,c)
    pe=magnitude(pa,pb,phase)
    pti=2*np.minimum(np.linalg.norm(pa,axis=1),np.linalg.norm(pb,axis=1))
    best.update(max_field_V_m=float(e.max()),
        sqrt_half_target_area_cm=float(np.sqrt(np.count_nonzero(pe>=.5*best['target_V_m'])*step**2)*100),
        current_per_coil_for_12_V_m_A=c.peak_current*12/best['target_V_m'],
        current_per_coil_for_100_V_m_A=c.peak_current*100/best['target_V_m'])
    result=dict(config=asdict(c),grid_step_m=step,voxel_count=len(points),best=best,
        central_field_V_m=float(magnitude(*fields(np.zeros((1,3)),c),0)[0]),
        same_frequency_sweep=rows,
        heating_examples=dict(
          rf_balanced_envelope_12_sigma1_sar_W_kg=1.*12**2/(4*c.density),
          lf_peak_100_pulsed_sar_W_kg=float(sar(100,c)),
          lf_peak_12_pulsed_sar_W_kg=float(sar(12,c))),
        ti=dict(target_envelope_V_m=ti_target,
          sqrt_half_target_area_cm=float(np.sqrt(np.count_nonzero(pti>=.5*ti_target)*step**2)*100),
          current_per_coil_for_12_V_m_A=c.peak_current*12/ti_target,
          current_per_coil_for_100_V_m_A=c.peak_current*100/ti_target,half_target_volume_cm3=vol*1e6,
          equivalent_sphere_diameter_cm=2*(3*vol/(4*np.pi))**(1/3)*100,
          target_to_max=float(ti_target/ti.max()),max_continuous_sar_W_kg=float(ti_sar.max()),
          target_at_sar_budget_V_m=float(ti_target*np.sqrt(c.sar_budget/ti_sar.max()))))
    return result,points,e,ti
