"""Local subject runner and read-only project inventory; no binary-coordinate decoding."""
import json
from pathlib import Path
import sqlite3
import pyvista as pv
import numpy as np
from src.positional import project, summarize
from src.subject_coordinates import file_hash, load_native
from src.subject_ingest import validate_id


def project_inventory(path):
    """Inspect names/schema only, on a recognized SQLite schema, without BLOB decoding."""
    result=dict(format='unknown', planned_names=[], coordinate_support='requires Brainsight target text export')
    with Path(path).open('rb') as stream:
        if stream.read(16) != b'SQLite format 3\x00': return result
    result['format']='SQLite'
    with sqlite3.connect(Path(path).resolve().as_uri()+'?mode=ro',uri=True) as db:
        tables={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if 'ZTARGETNODE' in tables:
            columns={r[1] for r in db.execute('PRAGMA table_info(ZTARGETNODE)')}
            if {'ZNAME','ZISLEAF'} <= columns:
                result['planned_names']=[r[0] for r in db.execute('SELECT ZNAME FROM ZTARGETNODE WHERE ZISLEAF=1')]
    return result


def subject_report(subject, root=Path('.')):
    """Available physical projections plus explicit missing-data rows; no fake distances."""
    validate_id(subject)
    root=Path(root)
    derivatives=root/'saves/derivatives/subjects'/subject
    markers=json.loads((derivatives/'markers.json').read_text())
    if markers.get('space')!='RAS_mm': raise ValueError('Markers must be native RAS mm')
    names=[m['name'] for m in markers['fiducials']]
    if len(set(names))!=len(names): raise ValueError('Duplicate marker identity')
    scalp_path=derivatives/'scalp.vtp'
    mesh=pv.read(scalp_path)
    manifest=json.loads((derivatives/'manifest.json').read_text())
    marker_mri=Path(manifest['input_paths']['anatomical'])
    if not marker_mri.is_absolute(): marker_mri=root/marker_mri
    load_native(marker_mri)
    if file_hash(marker_mri)!=markers['source_sha256']: raise ValueError('Marker MRI identity changed; rerun ingestion')
    provenance=dict(context=dict(marker_mri_sha256=markers['source_sha256']),
                    mode='local-input-QC',scalp_sha256=file_hash(scalp_path),
                    markers_sha256=file_hash(derivatives/'markers.json'))
    cap_points=[]
    for m in markers['fiducials']:
        q,d=project(mesh,m['position'])
        cap_points.append(dict(name=m['name'],label=m.get('anatomical_label') or m['label'],
                               raw=m['position'],scalp=q,projection_distance_mm=d))
    base=root/'saves/brainsight/restore'/subject
    projects=sorted(base.glob('*.bsproj')); images=sorted(base.glob('*.nii*'))
    inventory=project_inventory(projects[0]) if len(projects)==1 else dict(planned_names=[])
    blockers=[]
    brainsight=None
    exports=sorted((base/'exports').glob('*.txt'))
    if len(exports)==1 and len(images)==1:
        brainsight=source_targets(exports[0],images[0],projects[0] if len(projects)==1 else None,derivatives/'brainsight')
        from src.brainsight_registration import register
        from src.subject_coordinates import apply_affine
        registration=register(images[0],marker_mri,derivatives/'brainsight/registration')
        matrix=np.array(registration['matrix'])
        overlay=pv.read(derivatives/'brainsight/scalp.ply').transform(matrix,inplace=False)
        overlay.save(derivatives/'brainsight/registered-scalp.ply')
        brainsight.update(frame='cap_MRI_RAS_mm',marker_mri_sha256=markers['source_sha256'],registration=registration,
                          display='registered physical overlay in cap MRI RAS mm; no display offset')
        for target in brainsight['targets']:
            target['position_source']=target['position']
            target['position']=apply_affine(matrix,target['position_source']).tolist()
            if target.get('orientation_export') is not None:
                target['orientation_cap']=(matrix[:3,:3]@np.array(target['orientation_export'])).tolist()
            projected,offset=project(mesh,target['position'])
            target['exploratory_scalp_projection']=dict(position=projected,distance_mm=offset,method='closest scalp triangle; exploratory only',qc='not a verified scalp-entry point')
            target['raw_offset_to_common_scalp_mm']=offset
            target['point_semantics']='unresolved: export has coordinates/orientation but no scalp-contact designation'
            target['scalp_point_qc']='off_common_scalp' if offset>.1 else 'near_scalp_semantics_still_unverified'
        provenance['registration']=registration
        inventory['planned_names']=[t['name'] for t in brainsight['targets']]
        review_path=base/'comparison/review.json'
        review=json.loads(review_path.read_text()) if review_path.exists() else {}
        provenance['review']=review
        if not review_path.exists():
            template=dict(source_mri_sha256=registration['source_sha256'],marker_mri_sha256=registration['target_sha256'],
                          mappings={site:dict(marker=None,brainsight=None,confirmed=False,evidence='') for site in ('SMA','right_DLPFC')},
                          semantics={t['name']:dict(frame='source_MRI_RAS_mm',verified=False,evidence='') for t in brainsight['targets']})
            (base/'comparison').mkdir(exist_ok=True)
            (base/'comparison/review-template.json').write_text(json.dumps(template,indent=2))
        from src.common_skin import build_common_skin
        from src.positional import sma_projected_metric
        mapping=review.get('mappings',{}).get('SMA',{})
        confirmed=next((m for m in markers['fiducials'] if m['name']==mapping.get('marker')),None)
        selected_skin=None
        projection_metric=None
        if confirmed is not None and mapping.get('confirmed') is True:
            mesh,selected_skin=build_common_skin(images[0],marker_mri,matrix,mesh,brainsight['targets'],confirmed['position'],derivatives/'common-skin')
            provenance['common_skin']=selected_skin
            provenance['scalp_sha256']=selected_skin['surface_sha256']
            for point in cap_points:
                point['scalp'],point['projection_distance_mm']=project(mesh,point['raw'])
            for target in brainsight['targets']:
                q,offset=project(mesh,target['position'])
                target['exploratory_scalp_projection'].update(position=q,distance_mm=offset,qc='diagnostic variant' if target['name']!='SMA' else 'projection endpoint, surface review required')
                target['raw_offset_to_common_scalp_mm']=offset
            projection_metric=sma_projected_metric(mesh,markers,brainsight['targets'],review,registration,selected_skin)
        from src.positional import reviewed_rows
        rows=reviewed_rows(subject,mesh,markers,brainsight,review,provenance)
    else:
        blockers.append('Exactly one planned-target text export and anatomical MRI are required.')
        rows=[dict(subject=subject,target=site,cap_label='F4' if site=='right_DLPFC' else 'SMA',
                   measurement='scalp-entry localization difference (mm)',qc='invalid',reason=blockers[0],provenance=provenance)
              for site in ('SMA','right_DLPFC')]
    blockers=list(dict.fromkeys(r['reason'] for r in rows if r['qc']!='valid'))
    return dict(frame='native_RAS_mm',status='complete' if all(r['qc']=='valid' for r in rows) else 'needs_review',
                rows=rows,summary=summarize(rows),cap_points=cap_points,project_inventory=inventory,
                blockers=blockers,brainsight=brainsight,sma_projection=locals().get('projection_metric'),common_skin=locals().get('selected_skin'))


def save_subject_report(subject, root=Path('.')):
    from src.positional import write_results
    result=subject_report(subject,root)
    output=Path(root)/'saves/derivatives/subjects'/subject/'positional'
    write_results(result['rows'],output)
    if result.get('sma_projection'):
        import csv
        row=result['sma_projection']
        with output.with_name('positional-projection.csv').open('w') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(row));writer.writeheader()
            writer.writerow({k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in row.items()})
    output.with_suffix('.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    return result,output.with_suffix('.json')


def assign_target(name):
    """Conservative named-site assignment; preserve variants, never use order or proximity."""
    import re
    words=re.sub(r'[^a-z0-9]+',' ',name.lower()).strip().split()
    if 'sma' in words:
        return 'SMA'
    if 'f4' in words or ('right' in words and 'dlpfc' in words):
        return 'right_DLPFC'
    return None


def source_targets(export, anatomical, project_path, output):
    """Targets and scalp in the *source* MRI frame, no cross-MRI overlay/measurement."""
    from efield.brainsight import read_export
    from src.positional import read_targets
    from src.head_surface import scalp_surface
    from src.export_web import web_mesh
    volume,affine,meta=load_native(anatomical)
    source_hash=file_hash(anatomical)
    coord=read_export(export).coord_sys
    context=dict(coordinate_system=coord,source_mri_sha256=source_hash,marker_mri_sha256=source_hash,
                 nifti_qform_code=meta['qform_code'],nifti_sform_code=meta['sform_code'],qform_sform_agree=True,
                 frame_evidence='Supplied project anatomical NIfTI; coded matching native forms validated by load_native; source-only display')
    imported=read_targets(project_path or export,context,export if project_path else None)
    for target in imported['targets']:
        target['internal_target']=assign_target(target['name'])
        target['mapping_method']='explicit name tokens; variant preserved' if target['internal_target'] else 'unassigned name'
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    stamp=output/'surface.json';mesh_path=output/'scalp.ply'
    key=dict(source_mri_sha256=source_hash,method='scalp_surface_v1')
    if not (stamp.exists() and mesh_path.exists() and json.loads(stamp.read_text())==key):
        mesh=scalp_surface(volume,affine)
        web_mesh(mesh).save(mesh_path)
        stamp.write_text(json.dumps(key))
    return dict(frame='source_MRI_RAS_mm',source_mri_sha256=source_hash,
                display='separate source anatomy; no cross-MRI registration applied',
                targets=imported['targets'],provenance=imported['provenance'])
