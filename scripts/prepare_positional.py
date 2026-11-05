"""Inventory local r-02 inputs without guessing mappings or reading project fields."""
import json
from pathlib import Path
from src.subject_coordinates import file_hash

base=Path('saves/brainsight/restore/r-02')
projects=list(base.glob('*.bsproj')); images=list(base.glob('*.nii*'))
if len(projects)!=1 or len(images)!=1: raise ValueError('Expected one project and one anatomical NIfTI')
for name in ('exports','comparison','validation'): (base/name).mkdir(exist_ok=True)
s=dict(subject='r-02',entry='../'+projects[0].name,source_mri='../'+images[0].name,
       marker_mri='REPLACE_WITH_MARKER_MRI_PATH',export='../exports/planned-targets.txt',
       scalp='REPLACE_WITH_FULL_NATIVE_SCALP_VTP',scalp_sha256='REPLACE',surface_kind='scalp',surface_review_evidence='',
       markers='REPLACE_WITH_SAVED_MARKERS_JSON',context=dict(coordinate_system='NIfTI:Q:Scanner',
       source_mri_sha256=file_hash(images[0]),marker_mri_sha256='REPLACE',frame_evidence=''),
       mappings={site:dict(marker='REPLACE_EXACT_MARKER_NAME',brainsight='REPLACE_EXACT_TARGET_NAME') for site in ('SMA','right_DLPFC')},semantics={})
p=base/'comparison/manifest.pending.json'
if p.exists(): raise ValueError('Pending manifest already exists; preserving edits')
p.write_text(json.dumps(dict(subjects=[s]),indent=2))
print('Created local pending manifest. Review and complete required fields before running.')
