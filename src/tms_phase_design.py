"""Two arbitrary vacuum loops, constrained amplitude/phase design, SI units.

This is a primary induction-field model, not an anatomical head solver.
"""
from dataclasses import dataclass, asdict
import numpy as np
from src.emvelop_feasibility import grid

@dataclass(frozen=True)
class Loop:
    center: tuple
    normal: tuple = (1., 0., 0.)
    radius: float = .05


def loop_nodes(loop, segments=128):
    n=np.array(loop.normal,dtype=float); n/=np.linalg.norm(n)
    reference=np.eye(3)[np.argmin(np.abs(n))]
    u=np.cross(n,reference); u/=np.linalg.norm(u); v=np.cross(n,u)
    theta=(np.arange(segments)+.5)*2*np.pi/segments
    radial=np.cos(theta)[:,None]*u+np.sin(theta)[:,None]*v
    tangent=-np.sin(theta)[:,None]*u+np.cos(theta)[:,None]*v
    return np.array(loop.center)+loop.radius*radial, loop.radius*2*np.pi/segments*tangent


def loop_field(points, loop, frequency=3000., segments=128):
    """Real E basis in V/m per peak kA; common temporal -i factor omitted."""
    source,dl=loop_nodes(loop,segments); out=np.empty((len(points),3))
    for start in range(0,len(points),1024):
        r=np.linalg.norm(np.asarray(points)[start:start+1024,None]-source,axis=-1)
        if np.any(r<1e-10): raise ValueError('Observation intersects filament')
        out[start:start+1024]=1e-7*2*np.pi*frequency*1000*np.einsum('ps,sk->pk',1/r,dl)
    return out


def vector_peak(field):
    """Exact max_t |Re(E exp(iwt))|, also valid for elliptical polarization."""
    a=field.real; b=field.imag
    aa=np.sum(a*a,axis=-1); bb=np.sum(b*b,axis=-1); ab=np.sum(a*b,axis=-1)
    return np.sqrt(np.maximum(0,.5*(aa+bb+np.sqrt((aa-bb)**2+4*ab**2))))


def constrained_weights(basis, target_row, ridge=0.):
    """min w^H Q w subject to h w=1, with dimensionless trace-scaled ridge."""
    g=np.asarray(basis).reshape(-1,2); q=g.conj().T@g/len(basis)
    q=q+ridge*np.trace(q).real/2*np.eye(2)
    h=np.asarray(target_row,dtype=complex)
    if np.linalg.norm(h)<1e-12: raise ValueError('Target orientation is unreachable')
    # Moore-Penrose solution handles identical loops; verify target independently.
    v=np.linalg.pinv(q,rcond=1e-12)@h.conj()
    w=v/(h@v)
    return w,q


def metrics(basis,w,step,duty=.002,sigma=.2,rho=1000.):
    field=np.einsum('pdk,k->pd',basis,w); peak=vector_peak(field)
    sar=sigma*duty*np.sum(abs(field)**2,axis=-1)/(2*rho)
    volume=np.count_nonzero(peak>=.5)*step**3
    return dict(half_target_volume_cm3=float(volume*1e6),
      cube_root_half_target_volume_cm=float(100*volume**(1/3)),
      equivalent_diameter_cm=float(200*(3*volume/(4*np.pi))**(1/3)),
      max_peak_per_unit_target=float(peak.max()),max_sar_per_unit_target=float(sar.max()),
      target_at_2Wkg=float(np.sqrt(2/sar.max())),
      target_at_5kA_each=float(5/max(abs(w))),
      current_kA_for_100Vm=(100*abs(w)).tolist(),phase_deg=np.angle(w,deg=True).tolist(),
      weights_kA_real=w.real.tolist(),weights_kA_imag=w.imag.tolist())


def geometries():
    loops=[]
    for side in (-1,1):
        options=[]
        for y in (-.03,0.,.03):
            for tilt in (-15.,0.,15.):
                t=np.deg2rad(tilt)
                options.append(Loop((side*.11,y,0.),(np.cos(t),np.sin(t),0.)))
        loops.append(options)
    return loops


def search(step=.006):
    points=grid(step,.075); target=np.zeros((1,3)); direction=np.array([0,0,1])
    options=geometries(); caches=[[loop_field(points,l) for l in side] for side in options]
    targets=[[loop_field(target,l)[0]@direction for l in side] for side in options]
    outside=np.linalg.norm(points,axis=1)>.01; rows=[]
    for i,left in enumerate(options[0]):
        for j,right in enumerate(options[1]):
            basis=np.stack((caches[0][i],caches[1][j]),axis=-1)
            h=np.array((targets[0][i],targets[1][j]))
            if np.linalg.norm(h)<1e-12: continue
            for ridge in (0.,.01,1.):
                w,q=constrained_weights(basis[outside],h,ridge)
                row=dict(left=asdict(left),right=asdict(right),ridge=ridge,
                    target_constraint_residual=float(abs(h@w-1)),objective=float(np.vdot(w,q@w).real),
                    **metrics(basis,w,step))
                rows.append(row)
    best=min(rows,key=lambda r:(r['half_target_volume_cm3'],-r['target_at_5kA_each']))
    return rows,best


def evaluate(row,step=.003):
    points=grid(step,.075)
    loops=[Loop(**row[k]) for k in ('left','right')]
    basis=np.stack([loop_field(points,l,segments=256) for l in loops],axis=-1)
    w=np.array(row['weights_kA_real'])+1j*np.array(row['weights_kA_imag'])
    result=metrics(basis,w,step)
    axis=np.arange(-.075,.075+step*.1,step); xx,yy=np.meshgrid(axis,axis,indexing='ij')
    plane=np.column_stack((xx.ravel(),yy.ravel(),np.zeros(xx.size)))
    mask=np.linalg.norm(plane,axis=1)<=.075+1e-10
    pb=np.stack([loop_field(plane,l,segments=256) for l in loops],axis=-1)
    pe=vector_peak(np.einsum('pdk,k->pd',pb,w)); pe[~mask]=np.nan
    result['sqrt_half_target_area_cm']=float(100*np.sqrt(np.count_nonzero(pe>=.5)*step**2))
    result['grid_step_m']=step
    return result,axis,pe.reshape(xx.shape),loops
