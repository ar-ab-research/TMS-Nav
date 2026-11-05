"""Run with a reviewed manifest; no automatic anatomical labels or target inference."""
import argparse
import json
from pathlib import Path
import pyvista as pv
from src.positional import read_targets, compare, write_results, validate_exports
from src.subject_coordinates import file_hash, load_native


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--validate-export', type=Path)
    parser.add_argument('--decimals', type=int, default=4)
    args=parser.parse_args()
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

if __name__=='__main__': main()
