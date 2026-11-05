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
                   provenance=imported['provenance'])
        try:
            marker = markers[mapping['marker']]
            target = next(t for t in imported['targets'] if t['name']==mapping['brainsight'])
            row.update(marker_name=mapping['marker'], brainsight_name=target['name'],
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
