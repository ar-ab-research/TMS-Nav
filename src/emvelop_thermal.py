"""Steady temperature-rise model on a voxelized insulating region.

Homogeneous illustrative perfusion; not patient dosimetry or compliance testing.
"""
import numpy as np
from scipy.sparse import coo_matrix, eye
from scipy.sparse.linalg import cg


def steady_temperature(points, heat_source, step, conductivity=.5, perfusion_sink=10000.):
    """Solve (-k Laplacian + b) deltaT = q, zero outer normal heat flux.

    points: regular Cartesian occupied voxels (m); q: W/m^3; k: W/m/K;
    b=rho_b*c_b*omega_b: W/m^3/K. Missing neighbors are insulated faces.
    """
    points=np.asarray(points); q=np.asarray(heat_source,float)
    if step<=0 or conductivity<=0 or perfusion_sink<=0 or q.shape!=(len(points),):
        raise ValueError('Positive coefficients and one source per voxel required')
    indices=np.rint((points-points.min(axis=0))/step).astype(int)
    if not np.allclose(points,indices*step+points.min(axis=0),atol=1e-8):
        raise ValueError('Points must lie on a regular grid')
    lookup={tuple(p):i for i,p in enumerate(indices)}
    if len(lookup)!=len(points): raise ValueError('Duplicate voxel')
    rows=[]; cols=[]; data=[]
    coefficient=conductivity/step**2
    for i,p in enumerate(indices):
        for axis in range(3):
            neighbor=p.copy(); neighbor[axis]+=1
            j=lookup.get(tuple(neighbor))
            if j is not None:
                rows.extend([i,j,i,j]); cols.extend([i,j,j,i]); data.extend([coefficient,coefficient,-coefficient,-coefficient])
    matrix=coo_matrix((data,(rows,cols)),shape=(len(points),len(points))).tocsr()+perfusion_sink*eye(len(points),format='csr')
    temp,info=cg(matrix,q,rtol=1e-10,atol=1e-12)
    if info: raise RuntimeError(f'Heat solve failed: {info}')
    residual=np.linalg.norm(matrix@temp-q)/max(np.linalg.norm(q),1e-30)
    return temp,dict(relative_residual=float(residual),energy_balance_relative=float(abs(perfusion_sink*temp.sum()-q.sum())/max(abs(q.sum()),1e-30)))
