"""Aim 1 positional comparisons. All computation is in native MRI RAS mm."""
import csv
import json
from pathlib import Path
import numpy as np
import pyvista as pv
from efield.brainsight import read_export, COL_LOC, COL_MAT
from src.subject_coordinates import apply_affine, validate_matrix, file_hash


def vector(p):
    p = np.asarray(p, float)
    if p.shape != (3,) or not np.isfinite(p).all():
        raise ValueError('Expected finite xyz')
    return p


def normalize(p, frame):
    """Explicit source coordinates to RAS mm; voxel affine must include mm units."""
    p = vector(p)
    axes, units = frame['axes'], frame['units']
    if axes == 'voxel':
        if units != 'index':
            raise ValueError('Voxel coordinates require index units')
        return apply_affine(validate_matrix(frame['voxel_to_ras_mm']), p)
    scale = {'mm': 1, 'meter': 1000, 'micron': .001}.get(units)
    if axes not in ('RAS', 'LPS') or scale is None:
        raise ValueError('Unresolved axes or units')
    return p * scale * ([-1, -1, 1] if axes == 'LPS' else np.ones(3))


def read_targets(entry, context, export=None):
    """.bsproj entry uses an explicitly supplied text fallback, never binary guesses."""
    entry = Path(entry)
    if entry.suffix == '.bsproj' and export is None:
        raise ValueError('Direct .bsproj retrieval unavailable: supply planned-target text export and verified context')
    path = Path(export) if export else entry
    ex = read_export(path)
    if ex.version not in (12, 14):
        raise ValueError('Supported text format versions: 12, 14')
    if ex.coord_sys != context['coordinate_system']:
        raise ValueError('Export frame differs from verified context')
    legacy_scanner = (ex.coord_sys == 'NIfTI:Scanner' and context.get('nifti_qform_code') == 1
                      and context.get('nifti_sform_code') in (0, 1) and context.get('qform_sform_agree') is True)
    if not (ex.coord_sys == 'NIfTI:Aligned' or ex.coord_sys.startswith('NIfTI:Q:') or legacy_scanner):
        raise ValueError('Use documented NIfTI Aligned/Q export; internal Brainsight space unresolved')
    if not any('Units: millimetres' in h for h in ex.header):
        raise ValueError('Export must explicitly declare millimetres')
    source, dest = context['source_mri_sha256'], context['marker_mri_sha256']
    if len(source) != 64 or len(dest) != 64 or not context.get('frame_evidence'):
        raise ValueError('MRI identities and frame evidence required')
    transform = np.eye(4)
    if source != dest:
        reg = context.get('registration', {})
        if not (reg.get('verified') is True and reg.get('source_sha256') == source
                and reg.get('target_sha256') == dest and reg.get('evidence')):
            raise ValueError('Different MRI requires verified source-to-marker RAS mm registration')
        transform = validate_matrix(reg['matrix'])
    targets = []
    for row in ex.targets:
        p = vector([float(row[c]) for c in COL_LOC])
        orientation = None
        if all(row.get(c) for c in COL_MAT):
            orientation = np.array([[float(row[f'm{c}n{r}']) for c in range(3)] for r in range(3)])
            if not np.isfinite(orientation).all():
                raise ValueError('Nonfinite orientation')
            orientation = orientation.tolist()
        targets.append(dict(name=row['Target Name'], raw_export_position=p.tolist(),
                            position=apply_affine(transform, p).tolist(), orientation_export=orientation,
                            fields=row))
    if len({t['name'] for t in targets}) != len(targets):
        raise ValueError('Duplicate target names require disambiguation')
    return dict(targets=targets, provenance=dict(mode='target-text-export-fallback',
        project=str(entry) if entry.suffix == '.bsproj' else None,
        export_sha256=file_hash(path), version=ex.version, header=ex.header,
        context=context, source_to_marker_ras_mm=transform.tolist()), samples_excluded=len(ex.samples))


def scalp(mesh):
    if not mesh.is_all_triangles or not mesh.n_cells or not np.isfinite(mesh.points).all():
        raise ValueError('Finite nonempty triangle scalp required')
    return mesh


def project(mesh, p):
    mesh = scalp(mesh)
    _, q = mesh.find_closest_cell(vector(p), return_closest_point=True)
    q = np.asarray(q).reshape(3)
    return q.tolist(), float(np.linalg.norm(vector(p)-q))


def entry_point(mesh, trajectory):
    """Verified external-to-internal segment; never infer an axis from orientation."""
    if not trajectory.get('verified') or not trajectory.get('evidence'):
        raise ValueError('Trajectory semantics/direction unverified')
    mesh = scalp(mesh)
    if mesh.n_open_edges:
        raise ValueError('Scalp is open: intersection anatomically ambiguous')
    a, b = vector(trajectory['outside']), vector(trajectory['inside'])
    probes = pv.PolyData(np.array([a,b])).select_enclosed_points(mesh, tolerance=0.000001)
    if list(probes['SelectedPoints']) != [0,1]:
        raise ValueError('Trajectory must start outside and end inside scalp')
    hits, _ = mesh.ray_trace(a,b)
    unique = []
    for h in hits:
        if not any(np.linalg.norm(h-q)<1e-5 for q in unique): unique.append(h)
    if len(unique) != 1:
        raise ValueError('Missing or ambiguous scalp intersection')
    return unique[0].tolist()


def compare(subject, mesh, markers, imported, mappings, semantics):
    if set(mappings) != {'SMA','right_DLPFC'}:
        raise ValueError('Explicit SMA and right_DLPFC mappings required')
    rows = []
    for site, mapping in mappings.items():
        row = dict(subject=subject, target=site, cap_label='F4' if site=='right_DLPFC' else 'SMA',
                   method='closest scalp triangle / verified trajectory entry', qc='invalid',
                   measurement='scalp-entry localization difference (mm)',
                   provenance=imported['provenance'])
        try:
            if mapping.get('confirmed') is not True or not mapping.get('evidence'):
                raise ValueError('Confirmed marker-to-target mapping with evidence required')
            marker = markers[mapping['marker']]
            target = next(t for t in imported['targets'] if t['name']==mapping['brainsight'])
            row.update(mapping=mapping, marker_name=mapping['marker'], brainsight_name=target['name'],
                       eeg_raw=vector(marker).tolist(), brainsight_raw=target['position'], target_source=target)
            row['eeg_scalp'], row['projection_distance_mm'] = project(mesh, marker)
            semantic = semantics.get(target['name'], {})
            if semantic.get('documented_scalp_point') and semantic.get('evidence') and semantic.get('verified'):
                q, distance = project(mesh, target['position'])
                if distance > .1: raise ValueError('Documented scalp point is off scalp by >0.1 mm')
                row['brainsight_scalp'] = target['position']
                row['method'] = 'closest scalp triangle / documented scalp point'
            else:
                row['trajectory'] = semantic
                row['brainsight_scalp'] = entry_point(mesh, semantic)
            row.update(distance_mm=float(np.linalg.norm(np.array(row['eeg_scalp'])-row['brainsight_scalp'])), qc='valid')
            row['scalp_entry_localization_difference_mm']=row['distance_mm']
        except (KeyError, ValueError, StopIteration) as error:
            row['reason'] = str(error) or 'Mapped target missing'
        rows.append(row)
    return rows


def summarize(rows):
    result = {}
    for site in ('SMA','right_DLPFC'):
        valid = [r for r in rows if r['target']==site and r['qc']=='valid']
        if len({r['subject'] for r in valid}) != len(valid):
            raise ValueError('One observation per subject/target required')
        x = np.array([r['distance_mm'] for r in valid])
        result[site] = dict(n=len(x), mean=float(x.mean()) if len(x) else None,
            SD=float(x.std(ddof=1)) if len(x)>1 else None,
            median=float(np.median(x)) if len(x) else None,
            IQR=float(np.diff(np.percentile(x,[25,75]))[0]) if len(x) else None,
            excluded=[dict(subject=r['subject'],reason=r.get('reason')) for r in rows if r['target']==site and r['qc']!='valid'])
    return result


def write_results(rows, out):
    out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix('.json').write_text(json.dumps(dict(frame='native_RAS_mm', rows=rows, summary=summarize(rows)),indent=2,allow_nan=False))
    fields = sorted(set().union(*(r.keys() for r in rows)))
    with out.with_suffix('.csv').open('w') as f:
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader()
        w.writerows({k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in r.items()} for r in rows)


def validate_exports(a, b, decimals):
    """Independent export comparison in the same normalized frame; rounding bound."""
    a={t['name']:vector(t['position']) for t in a['targets']}
    b={t['name']:vector(t['position']) for t in b['targets']}
    if not a or a.keys()!=b.keys(): raise ValueError('Target names must match exactly')
    if not isinstance(decimals, int) or not 0 <= decimals <= 12:
        raise ValueError('Decimal precision must be an integer from 0 to 12')
    tolerance=float(np.sqrt(3)*10.**(-decimals))
    maximum=max(float(np.linalg.norm(a[k]-b[k])) for k in a)
    return dict(maximum_discrepancy_mm=maximum,tolerance_mm=tolerance,passed=maximum<=tolerance,
                interpretation='Numerical agreement only; anatomical and registration accuracy unvalidated')


def reviewed_rows(subject, mesh, markers, brainsight, review, provenance):
    """Gate primary measurements independently from registered raw visualization."""
    rows=[]
    reg=brainsight['registration']
    identities=(review.get('source_mri_sha256')==reg['source_sha256'] and
                review.get('marker_mri_sha256')==reg['target_sha256'])
    for site in ('SMA','right_DLPFC'):
        row=dict(subject=subject,target=site,cap_label='F4' if site=='right_DLPFC' else 'SMA',qc='invalid',
                 measurement='scalp-entry localization difference (mm)',provenance=provenance)
        candidates=[t for t in brainsight['targets'] if t['internal_target']==site]
        row['brainsight_candidates']=candidates
        issues=[]
        if not candidates:issues.append('Missing planned target for '+site)
        if candidates:
            if not identities:issues.append('No review bound to both MRI identities')
            if not reg.get('verified'):issues.append('Registration anatomical review is not confirmed')
            mapping=review.get('mappings',{}).get(site,{})
            if mapping.get('confirmed') is not True or not mapping.get('evidence'):
                issues.append('Cap marker-to-target mapping is unconfirmed')
            if not any(sem.get('verified') is True and sem.get('evidence') and
                       (sem.get('documented_scalp_point') or ('outside' in sem and 'inside' in sem))
                       for name,sem in review.get('semantics',{}).items() if name in [t['name'] for t in candidates]):
                issues.append('No documented scalp point or verified inward trajectory')
        row['qc_issues']=issues
        try:
            if not candidates:raise ValueError('Missing planned target for '+site)
            if not identities:raise ValueError('Review matching both MRI hashes and confirmed marker mapping required')
            if not reg.get('verified'):raise ValueError('Registration anatomical alignment review required')
            mapping=review.get('mappings',{}).get(site,{})
            if mapping.get('confirmed') is not True or not mapping.get('evidence'):
                raise ValueError('Confirmed marker-to-target mapping with evidence required')
            selected=next((t for t in candidates if t['name']==mapping.get('brainsight')),None)
            if selected is None:raise ValueError('Explicit planned target variant selection required')
            semantic=dict(review.get('semantics',{}).get(selected['name'],{}))
            if semantic.get('frame')=='source_MRI_RAS_mm':
                for k in ('outside','inside'):
                    if k in semantic:semantic[k]=apply_affine(reg['matrix'],vector(semantic[k])).tolist()
            elif semantic.get('frame')!='cap_MRI_RAS_mm':
                raise ValueError('Scalp/trajectory semantics require explicit source or cap MRI frame')
            maps={s:dict(mapping) if s==site else {} for s in ('SMA','right_DLPFC')}
            imported=dict(targets=[selected],provenance=provenance)
            computed=compare(subject,mesh,{m['name']:m['position'] for m in markers['fiducials']},imported,maps,{selected['name']:semantic})
            row.update(next(r for r in computed if r['target']==site))
        except ValueError as error:row['reason']=str(error)
        rows.append(row)
    return rows


def sma_projected_metric(mesh, markers, targets, review, registration, surface):
    """Explicit projection endpoint; trajectory/contact semantics are irrelevant."""
    row=dict(subject=markers.get('subject'),target='SMA',measurement='SMA scalp-projected localization difference (mm)',
             qc='unavailable',method='independent closest points on common skin mesh triangle interiors',
             surface=surface,registration=registration)
    try:
        mapping=review.get('mappings',{}).get('SMA',{})
        if review.get('marker_mri_sha256')!=registration['target_sha256'] or review.get('source_mri_sha256')!=registration['source_sha256']:
            raise ValueError('Confirmed mapping MRI identities mismatch')
        if mapping.get('confirmed') is not True or not mapping.get('evidence') or mapping.get('brainsight')!='SMA':
            raise ValueError('Explicit confirmed cap-SMA to exact Brainsight SMA mapping required')
        marker=next((m for m in markers['fiducials'] if m['name']==mapping['marker']),None)
        target=next((t for t in targets if t['name']=='SMA'),None)
        if marker is None or target is None:raise ValueError('Confirmed marker or SMA target missing')
        if registration.get('numerical_qc')!='passed':raise ValueError('Registration numerical QC failed')
        if not surface.get('surface_sha256') or surface.get('status') in ('rejected','invalid'):raise ValueError('Common skin surface identity/quality is unresolved')
        a,da=project(mesh,marker['position']);b,db=project(mesh,target['position'])
        row.update(marker_name=marker['name'],brainsight_name='SMA',mapping=mapping,
                   eeg_raw=marker['position'],brainsight_raw_source=target['position_source'],brainsight_raw_cap=target['position'],
                   eeg_projected=a,brainsight_projected=b,eeg_projection_offset_mm=da,brainsight_projection_offset_mm=db,
                   distance_mm=float(np.linalg.norm(np.array(a)-b)))
        reviewed=surface.get('verified') is True and registration.get('verified') is True
        warnings=[]
        if not surface.get('verified'):warnings.append('Skin-only boundary requires anatomical review: hair/skin ambiguity, artifacts and FOV edges; provisional preview only')
        if not registration.get('verified'):warnings.append('Registration anatomical review outstanding')
        accepted=reviewed and surface.get('review',{}).get('scope')=='user_visual_qc_acceptance'
        row.update(qc='reviewed' if accepted else 'verified' if reviewed else 'provisional',reason='User reviewed rendering and QC plots and accepted this result; independent clinical accuracy is not established.' if accepted else '; '.join(warnings))
    except (ValueError,KeyError) as error:row['reason']=str(error)
    return row
