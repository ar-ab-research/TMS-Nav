"""Cap-free intensity-boundary candidate; never silently mark skin verified."""
import json
from pathlib import Path
import numpy as np
from scipy import ndimage
from src.subject_coordinates import load_native, file_hash, apply_affine
from src.skull_boundary import otsu_air_threshold
from src.head_surface import scalp_surface
from src.projection_audit import discrepancy


def build_common_skin(source, cap, matrix, old_mesh, targets, marker, output):
    import pyvista as pv
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    volume,affine,_=load_native(source)
    key=dict(source_sha256=file_hash(source),matrix=np.asarray(matrix).tolist(),method='intensity_boundary_slice_fill_v2')
    stamp=output/'candidate.json';path=output/'common-skin.vtp'
    if stamp.exists() and json.loads(stamp.read_text()).get('cache_key')==key and path.exists():
        mesh=pv.read(path);data=json.loads(stamp.read_text())
    else:
        cut=otsu_air_threshold(volume)
        components,n=ndimage.label(volume>cut)
        sizes=np.bincount(components.ravel());sizes[0]=0
        mask=components==sizes.argmax()
        # Fill enclosed image-plane holes to remove internal skull/brain interfaces;
        # do not erode/close/offset the external intensity boundary.
        for axis in range(3):
            for index in range(mask.shape[axis]):
                section=[slice(None)]*3;section[axis]=index
                mask[tuple(section)]=ndimage.binary_fill_holes(mask[tuple(section)])
        mask=ndimage.binary_fill_holes(mask)
        # No erosion/opening/closing or cosmetic smoothing: contour image evidence.
        mesh=scalp_surface(volume,affine,mask=mask,smooth_sigma=0,smooth_iters=0)
        mesh=mesh.transform(matrix,inplace=False);mesh.save(path)
        data=dict(cache_key=key,threshold=float(cut),source='registered cap-free anatomical MRI',
                  method='air/tissue intensity threshold, largest connected tissue component, orthogonal image-plane enclosed-hole fill, unsmoothed 0.5 contour',
                  verified=False,status='provisional_requires_anatomical_review',
                  limitations=['T1 cannot establish histological skin/hair boundary everywhere','Cap-free status and regional skin boundary require anatomical review','Rigid registration and acquisition differences remain sources of uncertainty'],
                  surface_sha256=file_hash(path),surface_file=str(path),n_open_edges=int(mesh.n_open_edges))
        stamp.write_text(json.dumps(data,indent=2))
    qc_slices(source,cap,matrix,old_mesh,mesh,targets,marker,output/'skin-qc.png')
    from src.export_web import web_mesh
    web_mesh(mesh).save(output/'common-skin.ply')
    data['selected_audit']=discrepancy(mesh,targets,matrix)
    data['old_surface_audit']=discrepancy(old_mesh,targets,matrix)
    from src.projection_audit import independent_project
    from src.positional import project
    independent=independent_project(mesh,marker);q,_=project(mesh,marker)
    independent['vtk_discrepancy_mm']=float(np.linalg.norm(np.asarray(q)-independent['position']))
    data['eeg_projection_audit']=independent
    display=pv.read(output/'common-skin.ply')
    data['display_mesh_offsets_mm']={name:project(display,q)[1] for name,q in {'EEG':independent['position'],**{name:t['position'] for name,t in data['selected_audit']['targets'].items()}}.items()}
    data['audit_checks']=dict(units='MRI world millimeters',transform_application='source to cap exactly once',
       display_offsets_used=False,target_names=[t['name'] for t in targets],
       rigid_separation_pass=data['selected_audit'].get('status')=='diagnostic variant missing' or data['selected_audit'].get('rigid_preservation_error_mm',1)<1e-8)
    if not data['audit_checks']['rigid_separation_pass']:raise ValueError('Rigid transform failed target-separation audit')
    data['qc_image']='skin-qc.png'
    edges=mesh.extract_feature_edges(boundary_edges=True,non_manifold_edges=False,feature_edges=False,manifold_edges=False)
    if edges.n_points:
        ijk=apply_affine(np.linalg.inv(affine)@np.linalg.inv(matrix),edges.points)
        fov_fraction=float(np.mean(np.minimum(ijk,np.asarray(volume.shape)-1-ijk).min(1)<.6))
    else:fov_fraction=0.
    data['quality_checks']=dict(open_edge_vertices_on_fov_fraction=fov_fraction,full_resolution_triangles=int(mesh.n_cells),open_edges=int(mesh.n_open_edges),field_of_view_truncation_requires_review=bool(mesh.n_open_edges))
    # Verification must bind to exactly this mesh, not a stale prior candidate.
    review_path=output/'surface-review.json'
    review=json.loads(review_path.read_text()) if review_path.exists() else {}
    if review.get('surface_sha256')==data['surface_sha256'] and review.get('verified') is True and review.get('evidence'):
        data.update(verified=True,status='user_accepted_visual_qc' if review.get('scope')=='user_visual_qc_acceptance' else 'anatomically_reviewed',review=review)
    else:data.update(verified=False,status='provisional_requires_anatomical_review')
    (output/'audit.json').write_text(json.dumps(data,indent=2))
    return mesh,data


def qc_slices(source,cap,matrix,old,new,targets,marker,path,marker_label="Confirmed EEG SMA"):

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from src.positional import project
    scans=[load_native(cap),load_native(source)]
    fig,axes=plt.subplots(4,3,figsize=(15,16))
    positions=[np.asarray(marker),np.asarray(next(t['position'] for t in targets if t['name']=='SMA'))]
    for row in range(4):
        volume,affine,meta=scans[row//2]
        # Map both cap-frame meshes/points into each scan's native voxel frame.
        native=np.eye(4) if row<2 else np.linalg.inv(matrix)
        world_to_vox=np.linalg.inv(affine)@native
        ijk=apply_affine(world_to_vox,positions)
        for axis in range(3):
            center=ijk[row%2];index=int(np.clip(round(center[axis]),0,volume.shape[axis]-1))
            sl=np.take(volume,index,axis=axis).T;remaining=[k for k in range(3) if k!=axis]
            ax=axes[row,axis];ax.imshow(sl,origin='lower',cmap='gray',vmax=np.percentile(volume,99.5))
            for surf,color,label in ((old,'orange','Old head mask'),(new,'lime','Candidate skin')):
                pts=apply_affine(world_to_vox,surf.points);near=np.abs(pts[:,axis]-index)<.65
                ax.scatter(pts[near,remaining[0]],pts[near,remaining[1]],s=.2,c=color,label=label)
            for p,color,label in [(marker,'red',marker_label)]+[(t['position'],'cyan',t['name']) for t in targets]:
                xyz=apply_affine(world_to_vox,p);ax.scatter(xyz[remaining[0]],xyz[remaining[1]],c=color,s=15)
                # Label includes off-plane distance so crosshairs never imply an exact slice hit.
                ax.annotate(f'{label} ({xyz[axis]-index:+.1f} vox)',(xyz[remaining[0]],xyz[remaining[1]]),fontsize=6,color=color)
            ax.set_title(('Cap MRI' if row<2 else 'Source MRI')+f' axis {axis}, slice {index}');ax.set_xlim(center[remaining[0]]-70,center[remaining[0]]+70);ax.set_ylim(center[remaining[1]]-60,center[remaining[1]]+60)
    axes[0,0].legend(fontsize=7);fig.suptitle('Before/after boundary QC: orange old mask, green unsmoothed cap-free intensity boundary. Current review status is recorded in the report.')
    fig.tight_layout();fig.savefig(path,dpi=140);plt.close(fig)
