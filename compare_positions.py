"""Run with a reviewed manifest; no automatic anatomical labels or target inference."""
import argparse
import json
from pathlib import Path
import pyvista as pv
from src.positional import read_targets, compare, write_results, validate_exports
from src.subject_coordinates import file_hash, load_native


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path, nargs='?')
    parser.add_argument('--confirm-sma-marker', help='Explicitly confirm this saved marker as cap SMA paired to exact planned target SMA')
    parser.add_argument('--subject', help='Run a local subject; use reviewed comparison/manifest.json when present, otherwise produce input QC and cap projections')
    parser.add_argument('--out', type=Path)
    parser.add_argument('--validate-export', type=Path)
    parser.add_argument('--decimals', type=int, default=4)
    args=parser.parse_args()
    if args.subject:
        from src.subject_ingest import validate_id
        from src.positional_subject import save_subject_report
        validate_id(args.subject)
        if args.manifest: parser.error('Use either --subject or a manifest')
        if args.confirm_sma_marker:
            from efield.brainsight import read_export
            base=Path('saves/brainsight/restore')/args.subject
            markers=json.loads((Path('saves/derivatives/subjects')/args.subject/'markers.json').read_text())
            if args.confirm_sma_marker not in [m['name'] for m in markers['fiducials']]: parser.error('Marker not found')
            if 'SMA' not in [t['Target Name'] for t in read_export(base/'exports/planned-targets.txt').targets]: parser.error('Exact planned SMA target missing')
            images=list(base.glob('*.nii*'))
            if len(images)!=1:parser.error('Expected one source anatomical MRI')
            path=base/'comparison/review.json'
            review=json.loads(path.read_text()) if path.exists() else {}
            review.update(source_mri_sha256=file_hash(images[0]),marker_mri_sha256=markers['source_sha256'])
            review.setdefault('mappings',{})['SMA']=dict(marker=args.confirm_sma_marker,brainsight='SMA',confirmed=True,evidence='Explicit user confirmation via --confirm-sma-marker; exact planned SMA target selected')
            path.parent.mkdir(exist_ok=True);path.write_text(json.dumps(review,indent=2))
        candidate=Path('saves/brainsight/restore')/args.subject/'comparison/manifest.json'
        if candidate.exists():
            args.manifest=candidate
            args.out=args.out or Path('saves/derivatives/subjects')/args.subject/'positional'
        else:
            result, output=save_subject_report(args.subject)
            print(f'Report: {output}\nStatus: {result["status"]}\nCap projections: {len(result["cap_points"])}')
            if result.get('sma_projection'):
                metric=result['sma_projection'];print(f"{metric['measurement']}: {metric.get('distance_mm', 'unavailable')} [{metric['qc']}]")
            for blocker in result['blockers']: print('- '+blocker)
            print('Open the viewer, select this subject, then click Reload analysis in the right sidebar.')
            return
    if not args.manifest or not args.out: parser.error('Supply --subject, or MANIFEST --out OUTPUT')
    config=json.loads(args.manifest.read_text())
    def path(p): return args.manifest.parent / p
    rows=[]
    for s in config['subjects']:
        context=s['context']
        for key, field in [('source_mri','source_mri_sha256'),('marker_mri','marker_mri_sha256')]:
            image=path(s[key]); load_native(image)
            if file_hash(image)!=context[field]: raise ValueError('MRI hash mismatch')
        if s['surface_kind']!='scalp' or not s.get('surface_review_evidence'):
            raise ValueError('Reviewed scalp required; skull cannot substitute')
        if file_hash(path(s['scalp']))!=s['scalp_sha256']: raise ValueError('Scalp hash mismatch')
        imported=read_targets(path(s['entry']), context, path(s['export']) if s.get('export') else None)
        imported['provenance']['scalp_sha256']=s['scalp_sha256']
        imported['provenance']['surface_review_evidence']=s['surface_review_evidence']
        imported['provenance']['markers_sha256']=file_hash(path(s['markers']))
        markers=json.loads(path(s['markers']).read_text())
        if markers.get('space') != 'RAS_mm': raise ValueError('Markers must be native RAS mm')
        if markers.get('source_sha256')!=context['marker_mri_sha256']: raise ValueError('Marker MRI mismatch')
        # Only raw saved fiducial positions; no marker-order or Cz substitution.
        names=[m['name'] for m in markers['fiducials']]
        if len(set(names))!=len(names): raise ValueError('Duplicate marker identity')
        rows+=compare(s['subject'],pv.read(path(s['scalp'])),
                      {m['name']:m['position'] for m in markers['fiducials']},imported,s['mappings'],s.get('semantics',{}))
        if args.validate_export:
            other=read_targets(args.validate_export,context)
            print(json.dumps(validate_exports(imported,other,args.decimals)))
    write_results(rows,args.out)
    print(f'Results: {args.out.with_suffix(".json")}')
    print('Open viewer, select subject, and click Reload analysis.')

if __name__=='__main__': main()
