"""Local subject runner and read-only project inventory; no binary-coordinate decoding."""
import json
from pathlib import Path
import sqlite3
import pyvista as pv
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
    if not list((base/'exports').glob('*.txt')):
        blockers.append('Planned-target text export missing. Export Targets from Brainsight into exports/.')
    else:
        blockers.append('Text export found: complete comparison/manifest.json with reviewed frame and trajectory evidence, then run the manifest command.')
    blockers.append('SMA/F4 mapping missing: assign exact saved marker names; marker order is not a label.')
    if not any('dlpfc' in str(n).lower() or str(n).lower()=='f4' for n in inventory['planned_names']):
        blockers.append('No explicitly named right-DLPFC/F4 planned target found in project inventory; confirm or supply that target.')
    if len(images)==1:
        _,_,meta=load_native(images[0]);source_hash=file_hash(images[0])
        provenance['context']['source_mri_sha256']=source_hash
        inventory['source_mri_shape']=meta['shape']
        if source_hash!=markers['source_sha256']:
            blockers.append('Brainsight anatomy and marker MRI differ: a reviewed source-to-marker MRI registration is required.')
    blockers.append('Planned scalp point or inward trajectory semantics must be verified before comparing.')
    rows=[dict(subject=subject,target=site,cap_label='F4' if site=='right_DLPFC' else 'SMA',
               method='closest scalp triangle / planned scalp entry',qc='invalid',reason='; '.join(blockers),
               provenance=provenance) for site in ('SMA','right_DLPFC')]
    return dict(frame='native_RAS_mm',status='needs_inputs',rows=rows,summary=summarize(rows),
                cap_points=cap_points,project_inventory=inventory,blockers=blockers)


def save_subject_report(subject, root=Path('.')):
    from src.positional import write_results
    result=subject_report(subject,root)
    output=Path(root)/'saves/derivatives/subjects'/subject/'positional'
    write_results(result['rows'],output)
    output.with_suffix('.json').write_text(json.dumps(result,indent=2,allow_nan=False))
    return result,output.with_suffix('.json')
