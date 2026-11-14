"""Independent triangle-interior projection and source/registered distance audit."""
import numpy as np
from src.positional import vector, project
from src.subject_coordinates import apply_affine


def independent_project(mesh, point):
    """Exhaustive numpy triangle plane+edge minima, independent of VTK locator."""
    p=vector(point);tri=np.asarray(mesh.points)[mesh.faces.reshape(-1,4)[:,1:]]
    a,b,c=tri[:,0],tri[:,1],tri[:,2];u=b-a;v=c-a;w=p-a
    uu=(u*u).sum(1);vv=(v*v).sum(1);uv=(u*v).sum(1)
    den=uu*vv-uv*uv;valid=den>1e-15
    s=np.divide(vv*(w*u).sum(1)-uv*(w*v).sum(1),den,out=np.zeros(len(den)),where=valid)
    t=np.divide(uu*(w*v).sum(1)-uv*(w*u).sum(1),den,out=np.zeros(len(den)),where=valid)
    plane=a+s[:,None]*u+t[:,None]*v
    candidates=[plane]
    distances=[np.where(valid&(s>=0)&(t>=0)&(s+t<=1),((plane-p)**2).sum(1),np.inf)]
    for x,y in ((a,b),(b,c),(c,a)):
        edge=y-x;length=(edge*edge).sum(1)
        factor=np.clip(np.divide(((p-x)*edge).sum(1),length,out=np.zeros(len(length)),where=length>0),0,1)
        q=x+factor[:,None]*edge;candidates.append(q);distances.append(((q-p)**2).sum(1))
    ds=np.stack(distances);indices=ds.argmin(0);qs=np.stack(candidates)[indices,np.arange(len(a))]
    d=ds.min(0);best=int(d.argmin());q=qs[best]
    other=np.flatnonzero(np.linalg.norm(qs-q,axis=1)>=5.)
    competitor=int(other[d[other].argmin()]) if len(other) else None
    return dict(position=q.tolist(),distance_mm=float(np.sqrt(d[best])),triangle=best,
                competing_region=None if competitor is None else dict(position=qs[competitor].tolist(),distance_mm=float(np.sqrt(d[competitor])),
                  distance_gap_mm=float(np.sqrt(d[competitor])-np.sqrt(d[best])),minimum_region_separation_mm=5))


def discrepancy(mesh, targets, matrix):
    by={t['name']:t for t in targets}
    audits={}
    for name in ('SMA','SMA Skin'):
        if name not in by:continue
        t=by[name];ind=independent_project(mesh,t['position']);vtk,offset=project(mesh,t['position'])
        ind.update(vtk_position=vtk,vtk_offset_mm=offset,independent_discrepancy_mm=float(np.linalg.norm(np.array(vtk)-ind['position'])),
                   transform_once_error_mm=float(np.linalg.norm(apply_affine(matrix,t['position_source'])-t['position'])))
        audits[name]=ind
    if not {'SMA','SMA Skin'}<=by.keys():return dict(status='diagnostic variant missing',targets=audits)
    a,b=by['SMA'],by['SMA Skin']
    raw=float(np.linalg.norm(np.array(a['position_source'])-b['position_source']))
    transformed=float(np.linalg.norm(np.array(a['position'])-b['position']))
    projected=float(np.linalg.norm(np.array(audits['SMA']['position'])-audits['SMA Skin']['position']))
    return dict(raw_source_separation_mm=raw,raw_cap_separation_mm=transformed,rigid_preservation_error_mm=abs(raw-transformed),
                projected_separation_mm=projected,targets=audits,
                interpretation='Nearest-surface mapping can switch competing regions for interior points; inspect distance gaps and slice QC. No display coordinates enter computation.')
