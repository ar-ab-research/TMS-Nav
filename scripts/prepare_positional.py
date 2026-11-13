"""Fill known local subject paths/hashes; preserve review fields and never infer mappings."""
import argparse
import json
import os
from pathlib import Path
from src.subject_coordinates import file_hash
from src.subject_ingest import validate_id


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--subject',default='r-02');args=parser.parse_args();validate_id(args.subject)
    base=Path('saves/brainsight/restore')/args.subject
    projects=list(base.glob('*.bsproj')); images=list(base.glob('*.nii*'))
    if len(projects)!=1 or len(images)!=1: raise ValueError('Expected one project and one anatomical NIfTI')
    for name in ('exports','comparison','validation'): (base/name).mkdir(exist_ok=True)
    p=base/'comparison/manifest.pending.json'
    config=json.loads(p.read_text()) if p.exists() else dict(subjects=[{}])
    s=config['subjects'][0]
    derivative=Path('saves/derivatives/subjects')/args.subject
    manifest=json.loads((derivative/'manifest.json').read_text())
    marker_mri=Path(manifest['input_paths']['anatomical'])
    def rel(path): return os.path.relpath(path.resolve(),p.parent.resolve())
    # Fill only unknown placeholders, preserving all explicit user edits.
    def fill(obj,k,value):
        if not obj.get(k) or str(obj[k]).startswith('REPLACE'): obj[k]=value
    for k,value in dict(subject=args.subject,entry=rel(projects[0]),source_mri=rel(images[0]),
                        marker_mri=rel(marker_mri),export='../exports/planned-targets.txt',
                        scalp=rel(derivative/'scalp.vtp'),scalp_sha256=file_hash(derivative/'scalp.vtp'),
                        surface_kind='scalp',markers=rel(derivative/'markers.json')).items():fill(s,k,value)
    s.setdefault('surface_review_evidence','')
    context=s.setdefault('context',{})
    fill(context,'source_mri_sha256',file_hash(images[0]));fill(context,'marker_mri_sha256',file_hash(marker_mri))
    context.setdefault('coordinate_system','NIfTI:Q:Scanner');context.setdefault('frame_evidence','')
    s.setdefault('mappings',{site:dict(marker='REPLACE_EXACT_MARKER_NAME',brainsight='REPLACE_EXACT_TARGET_NAME') for site in ('SMA','right_DLPFC')})
    s.setdefault('semantics',{})
    p.write_text(json.dumps(config,indent=2));print('Known paths and hashes filled in pending manifest. Review fields and mappings remain explicit.')

if __name__=='__main__': main()
