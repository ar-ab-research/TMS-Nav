"""Homogeneous-medium RF reconstruction; not an anatomical EMvelop reproduction."""
from dataclasses import dataclass, asdict
import numpy as np
from scipy.linalg import null_space
from scipy.optimize import minimize
from scipy.ndimage import uniform_filter

MU0=4e-7*np.pi
EPS0=8.8541878128e-12
@dataclass
class RFConfig:
    frequency: float=1.5e9
    epsilon_r: float=50.
    conductivity: float=1.
    density: float=1000.
    radius: float=.075
    source_x: float=.085
    length: float=.01
    quadrature: int=8

def sources(c):
    yz=np.array([(y,z) for y in np.linspace(-.021,.021,4) for z in np.linspace(-.0235,.0235,3)])
    return [np.column_stack((np.full(12,x),yz)) for x in [-c.source_x,c.source_x]]

def transfer(points, centers, c):
    """Electric field per ampere: exact homogeneous dyadic, integrated finite line."""
    points=np.asarray(points); centers=np.asarray(centers)
    omega=2*np.pi*c.frequency
    k=np.sqrt(omega**2*MU0*EPS0*c.epsilon_r-1j*omega*MU0*c.conductivity)
    nodes,weights=np.polynomial.legendre.leggauss(c.quadrature)
    out=np.zeros((len(points),3,len(centers)),complex)
    for t,weight in zip(nodes,weights):
        psrc=centers+np.array([0,0,t*c.length/2])
        d=points[:,None,:]-psrc[None,:,:]
        r=np.linalg.norm(d,axis=-1)
        if np.min(r)<1e-8: raise ValueError('Point on source filament')
        u=d/r[...,None]; kr=k*r
        # radial Hessian: G'/r and G''-G'/r; exp(+i omega t).
        a=1-1j/kr-1/kr**2
        b=-1+3j/kr+3/kr**2
        v=b[...,None]*u*u[...,2,None]
        v[...,2]+=a
        v*=(-1j*omega*MU0*np.exp(-1j*kr)/(4*np.pi*r)*weight*c.length/2)[...,None]
        out+=v.transpose(0,2,1)
    return out

def grid(step,c):
    n=int(np.ceil(c.radius/step)); axis=np.arange(-n,n+1)*step
    xyz=np.stack(np.meshgrid(axis,axis,axis,indexing='ij'),axis=-1)
    mask=np.linalg.norm(xyz,axis=-1)<=c.radius+1e-12
    return xyz[mask],mask,axis

def basis(g):
    b=np.array([0,0,.5],complex)
    w=np.linalg.lstsq(g,b,rcond=None)[0]
    return w,null_space(g)

def optimize(g1,g2,t1,t2,seeds=3):
    """Minimize nonsmooth min-of-carrier powers with exact vector target constraints."""
    w1,z1=basis(t1); w2,z2=basis(t2)
    m1=z1.shape[1]; m2=z2.shape[1]; m=m1+m2
    base=[np.einsum('ncm,m->nc',g,w) for g,w in [(g1,w1),(g2,w2)]]
    h=[np.einsum('ncm,mk->nck',g,z) for g,z in [(g1,z1),(g2,z2)]]
    def unpack(x): return x[:m]+1j*x[m:]
    def objective(x):
        v=unpack(x); e1=base[0]+np.einsum('ncm,m->nc',h[0],v[:m1]); e2=base[1]+np.einsum('ncm,m->nc',h[1],v[m1:])
        p1=np.sum(abs(e1)**2,axis=1); p2=np.sum(abs(e2)**2,axis=1)
        active=p1<=p2
        grad=np.concatenate([np.einsum('ncm,nc->m',h[0][active].conj(),e1[active]),np.einsum('ncm,nc->m',h[1][~active].conj(),e2[~active])])*2/len(g1)
        return float(np.minimum(p1,p2).mean()),np.r_[grad.real,grad.imag]
    rng=np.random.default_rng(20261112); trials=[]; best=None
    scale=max(np.linalg.norm(w1),np.linalg.norm(w2))
    for seed in range(seeds):
        x=np.zeros(2*m) if seed==0 else rng.normal(size=2*m)*scale*.1
        sol=minimize(objective,x,jac=True,method='L-BFGS-B',options={'maxiter':400,'ftol':1e-11,'gtol':1e-7,'maxls':50})
        trials.append(dict(seed=seed,success=bool(sol.success),message=sol.message,iterations=sol.nit,objective=float(sol.fun),gradient_norm=float(np.linalg.norm(sol.jac))))
        if best is None or sol.fun<best.fun: best=sol
    v=unpack(best.x)
    return (w1,w2),(w1+z1@v[:m1],w2+z2@v[m1:]),trials,objective

def evaluate(g,weights,step,mask,c):
    es=[np.einsum('ncm,m->nc',a,w) for a,w in zip(g,weights)]
    power=[np.sum(abs(e)**2,axis=1) for e in es]
    envelope=2*np.sqrt(np.minimum(*power)); sar=c.conductivity*sum(power)/(2*c.density)
    volume=float(np.count_nonzero(envelope>=.5)*step**3) # target is 1 V/m by construction
    # Nominal cube mass nearest 10g; truncated boundary averages explicitly reported.
    count=max(1,int(round((.01/c.density)**(1/3)/step)))
    full=np.zeros(mask.shape); full[mask]=sar
    occupancy=uniform_filter(mask.astype(float),size=count,mode='constant')
    average=uniform_filter(full,size=count,mode='constant')/np.maximum(occupancy,1e-20)
    max_avg=float(average[mask].max())
    peak=float(sar.max()); scale=(10/max_avg)**.5
    return dict(cube_root_half_target_volume_cm=100*volume**(1/3),half_target_volume_cm3=volume*1e6,
      max_sar_for_unit_target_W_kg=peak,max_cube_average_sar_for_unit_target_W_kg=max_avg,
      cube_width_voxels=count,full_cube_mass_g=c.density*(count*step)**3*1000,
      target_at_pointwise_2Wkg_V_m=float((2/peak)**.5),target_at_cube_average_10Wkg_V_m=float(scale),
      max_field_envelope_for_unit_target_V_m=float(envelope.max())),envelope,sar
