import numpy as np
import pyvista as pv
import pytest
from src.positional import normalize, project, entry_point, compare, summarize, validate_exports, read_targets, write_results
from efield.brainsight import write_fixture


def test_frames():
    assert np.allclose(normalize([1,2,3],dict(axes='LPS',units='meter')),[-1000,-2000,3000])
    a=np.array([[0,-2,0,10],[3,0,0,20],[0,0,4,30],[0,0,0,1]])
    assert np.allclose(normalize([1,2,3],dict(axes='voxel',units='index',voxel_to_ras_mm=a)),[6,23,42])
    with pytest.raises(ValueError): normalize([0,0,0],dict(axes='unknown',units='mm'))
    with pytest.raises(ValueError): normalize([np.nan,0,0],dict(axes='RAS',units='mm'))


def test_triangle():
    mesh=pv.PolyData([[0.,0,0],[10,0,0],[0,10,0]],[3,0,1,2])
    q,d=project(mesh,[2,3,4]);assert np.allclose(q,[2,3,0]);assert d==4
    q,d=project(mesh,[-3,0,4]);assert np.allclose(q,[0,0,0]);assert d==5


def test_intersections():
    mesh=pv.Cube(bounds=(-10,10,-10,10,-10,10)).triangulate()
    t=dict(outside=[0,0,20],inside=[0,0,0],verified=True,evidence='synthetic inward segment')
    assert np.allclose(entry_point(mesh,t),[0,0,10])
    for invalid in [{},dict(t, outside=[0,0,0],inside=[0,0,20]),dict(t,inside=[0,0,-20])]:
        with pytest.raises(ValueError): entry_point(mesh,invalid)
    with pytest.raises(ValueError): entry_point(pv.Plane().triangulate(),t)


def test_pair_exports(tmp_path):
    mesh=pv.Cube(bounds=(-10,10,-10,10,-10,10)).triangulate()
    imported=dict(provenance={},targets=[dict(name='planned',position=[0,0,0])])
    mappings={s:dict(marker='cap',brainsight='planned',confirmed=True,evidence='synthetic identity') for s in ['SMA','right_DLPFC']}
    sem={'planned':dict(outside=[3,4,20],inside=[3,4,0],verified=True,evidence='synthetic')}
    rows=compare('synthetic',mesh,{'cap':[0,0,12]},imported,mappings,sem)
    assert all(r['distance_mm']==pytest.approx(5) for r in rows)
    assert rows[0]['eeg_raw']==[0,0,12]
    assert summarize(rows)['SMA']['n']==1
    write_results(rows,tmp_path/'result')
    assert (tmp_path/'result.csv').exists()
    invalid=compare('synthetic',mesh,{'cap':[0,0,12]},imported,mappings,{})
    assert summarize(invalid)['SMA']['n']==0
    assert all(r['qc']=='invalid' and 'distance_mm' not in r for r in invalid)
    with pytest.raises(ValueError):compare('s',mesh,{},imported,{}, {})


def test_adapter(tmp_path):
    p=write_fixture(tmp_path/'targets.txt',[])
    ctx=dict(coordinate_system='NIfTI:Aligned',source_mri_sha256='a'*64,marker_mri_sha256='a'*64,frame_evidence='synthetic header')
    assert read_targets(p,ctx)['targets']==[]
    with pytest.raises(ValueError):read_targets(tmp_path/'test.bsproj',ctx)
    with pytest.raises(ValueError):read_targets(p,dict(ctx,marker_mri_sha256='b'*64))
    reg=dict(verified=True,evidence='synthetic',source_sha256='a'*64,target_sha256='b'*64,matrix=np.eye(4).tolist())
    assert read_targets(p,dict(ctx,marker_mri_sha256='b'*64,registration=reg))
    a=dict(targets=[dict(name='x',position=[1,2,3])]);b=dict(targets=[dict(name='x',position=[1.0001,2,3])])
    assert validate_exports(a,b,4)['passed']
    assert not validate_exports(a,b,5)['passed']


def test_target_registration_and_samples_separate(tmp_path):
    from efield.poses import CoilPose
    target=CoilPose([1,2,3],[0,1,0],[0,0,1],name='individual planned')
    sample=CoilPose([90,90,90],[0,1,0],[0,0,1],name='recorded sample')
    p=write_fixture(tmp_path/'targets.txt',[sample],targets=[target])
    matrix=np.array([[0,-1,0,10],[1,0,0,20],[0,0,1,30],[0,0,0,1]])
    reg=dict(verified=True,evidence='known synthetic registration',source_sha256='a'*64,target_sha256='b'*64,matrix=matrix.tolist())
    ctx=dict(coordinate_system='NIfTI:Aligned',source_mri_sha256='a'*64,marker_mri_sha256='b'*64,frame_evidence='synthetic',registration=reg)
    data=read_targets(tmp_path/'test.bsproj',ctx,p)
    assert data['samples_excluded']==1 and len(data['targets'])==1
    assert data['targets'][0]['name']=='individual planned'
    assert data['targets'][0]['position']==[8,21,33]
    assert data['targets'][0]['raw_export_position']==[1,2,3]
    assert data['targets'][0]['orientation_export'] is not None


def test_project_inventory_does_not_decode_coordinates(tmp_path):
    import sqlite3
    from src.positional_subject import project_inventory
    path=tmp_path/'project.bsproj'
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE ZTARGETNODE(ZNAME TEXT, ZISLEAF INTEGER, ZPOSITION BLOB)')
        db.executemany('INSERT INTO ZTARGETNODE VALUES (?,?,?)',[('planned',1,b'not coordinates'),('folder',0,b'')])
    before=path.read_bytes()
    result=project_inventory(path)
    assert result['planned_names']==['planned']
    assert 'export' in result['coordinate_support']
    assert path.read_bytes()==before


def test_subject_input_qc_preserves_raw_markers(tmp_path):
    import json
    from src.synthetic_subject import make_phantom
    from src.subject_coordinates import file_hash
    from src.positional_subject import save_subject_report
    source,_=make_phantom(tmp_path/'inputs')
    output=tmp_path/'saves/derivatives/subjects/test'
    output.mkdir(parents=True)
    mesh=pv.Cube(bounds=(-10,10,-10,10,-10,10)).triangulate();mesh.save(output/'scalp.vtp')
    markers=dict(space='RAS_mm',source_sha256=file_hash(source),fiducials=[dict(name='unassigned',label='unassigned',position=[0,0,12])])
    (output/'markers.json').write_text(json.dumps(markers))
    (output/'manifest.json').write_text(json.dumps(dict(input_paths=dict(anatomical=str(source)))))
    result,path=save_subject_report('test',tmp_path)
    assert result['status']=='needs_review'
    assert result['cap_points'][0]['raw']==[0,0,12]
    assert result['cap_points'][0]['scalp']==[0,0,10]
    assert result['cap_points'][0]['projection_distance_mm']==2
    assert all(r['qc']=='invalid' and 'distance_mm' not in r for r in result['rows'])
    assert path.exists() and path.with_suffix('.csv').exists()
    assert json.loads((output/'markers.json').read_text())==markers


def test_autonomous_named_target_assignment():
    from src.positional_subject import assign_target
    assert assign_target('SMA')=='SMA'
    assert assign_target('SMA Skin')=='SMA'
    assert assign_target('Right DLPFC')=='right_DLPFC'
    assert assign_target('F4')=='right_DLPFC'
    assert assign_target('left DLPFC') is None
    assert assign_target('unknown') is None
    assert assign_target('preSMA') is None


def test_legacy_scanner_requires_validated_native_header(tmp_path):
    from efield.poses import CoilPose
    p=write_fixture(tmp_path/'scanner.txt',[],coord_sys='NIfTI:Scanner',
                    targets=[CoilPose([1,2,3],[0,1,0],[0,0,1],name='SMA Skin')])
    ctx=dict(coordinate_system='NIfTI:Scanner',source_mri_sha256='a'*64,marker_mri_sha256='a'*64,
             frame_evidence='coded scanner forms agree',nifti_qform_code=1,nifti_sform_code=1,qform_sform_agree=True)
    assert read_targets(p,ctx)['targets'][0]['position']==[1,2,3]
    with pytest.raises(ValueError):read_targets(p,dict(ctx,qform_sform_agree=False))
    with pytest.raises(ValueError):read_targets(p,dict(ctx,nifti_qform_code=2))


def test_registration_direction_and_lps_ras():
    import SimpleITK as sitk
    from src.brainsight_registration import ras_source_to_cap
    from src.subject_coordinates import RAS_LPS, apply_affine
    t=sitk.Euler3DTransform();t.SetRotation(.1,-.2,.3);t.SetTranslation((12.,-7.,4.))
    matrix=ras_source_to_cap(t)
    cap_ras=np.array([20.,30.,40.]);cap_lps=apply_affine(RAS_LPS,cap_ras)
    source_lps=np.array(t.TransformPoint(tuple(cap_lps)))
    assert np.allclose(apply_affine(matrix,apply_affine(RAS_LPS,source_lps)),cap_ras)
    assert not np.allclose(apply_affine(np.linalg.inv(matrix),apply_affine(RAS_LPS,source_lps)),cap_ras)


def test_reviewed_distance_and_missing_target():
    from src.positional import reviewed_rows
    mesh=pv.Cube(bounds=(-10,10,-10,10,-10,10)).triangulate()
    matrix=np.eye(4);matrix[0,3]=10
    reg=dict(verified=True,source_sha256='a'*64,target_sha256='b'*64,matrix=matrix.tolist())
    bs=dict(registration=reg,targets=[dict(name='planned',internal_target='SMA',position=[3,4,0])])
    markers=dict(fiducials=[dict(name='cap',position=[0,0,12])])
    review=dict(source_mri_sha256='a'*64,marker_mri_sha256='b'*64,
                mappings=dict(SMA=dict(marker='cap',brainsight='planned',confirmed=True,evidence='synthetic confirmation')),
                semantics={'planned':dict(frame='source_MRI_RAS_mm',outside=[-7,4,20],inside=[-7,4,0],verified=True,evidence='synthetic inward segment')})
    rows=reviewed_rows('s',mesh,markers,bs,review,{})
    assert rows[0]['scalp_entry_localization_difference_mm']==pytest.approx(5)
    assert rows[0]['measurement']=='scalp-entry localization difference (mm)'
    assert rows[1]['qc']=='invalid' and 'Missing planned target' in rows[1]['reason']
    review['mappings']['SMA']['confirmed']=False
    assert reviewed_rows('s',mesh,markers,bs,review,{})[0]['qc']=='invalid'
    review['mappings']['SMA']['confirmed']=True
    bs['registration']['verified']=False
    assert reviewed_rows('s',mesh,markers,bs,review,{})[0]['qc']=='invalid'


def test_name_does_not_establish_scalp_entry():
    from src.positional import reviewed_rows
    mesh=pv.Cube(bounds=(-10,10,-10,10,-10,10)).triangulate()
    reg=dict(verified=True,source_sha256='a'*64,target_sha256='b'*64,matrix=np.eye(4).tolist())
    bs=dict(registration=reg,targets=[dict(name='SMA Skin',internal_target='SMA',position=[0,0,0])])
    markers=dict(fiducials=[dict(name='cap',position=[0,0,12])])
    review=dict(source_mri_sha256='a'*64,marker_mri_sha256='b'*64,
                mappings=dict(SMA=dict(marker='cap',brainsight='SMA Skin',confirmed=True,evidence='synthetic')),
                semantics={'SMA Skin':dict(frame='cap_MRI_RAS_mm',documented_scalp_point=True,verified=True,evidence='synthetic claim')})
    rows=reviewed_rows('s',mesh,markers,bs,review,{})
    assert rows[0]['qc']=='invalid' and 'off scalp' in rows[0]['reason']


def test_exploratory_projection_never_becomes_entry():
    from src.positional import reviewed_rows
    mesh=pv.Cube(bounds=(-10,10,-10,10,-10,10)).triangulate()
    reg=dict(verified=True,source_sha256='a'*64,target_sha256='b'*64,matrix=np.eye(4).tolist())
    target=dict(name='SMA Skin',internal_target='SMA',position=[0,0,0],
                exploratory_scalp_projection=dict(position=[0,0,10],method='exploratory only'))
    review=dict(source_mri_sha256='a'*64,marker_mri_sha256='b'*64,
                mappings=dict(SMA=dict(marker='cap',brainsight='SMA Skin',confirmed=True,evidence='synthetic')))
    rows=reviewed_rows('s',mesh,dict(fiducials=[dict(name='cap',position=[0,0,12])]),
                       dict(registration=reg,targets=[target]),review,{})
    assert rows[0]['qc']=='invalid' and 'distance_mm' not in rows[0]
    assert 'No documented scalp point or verified inward trajectory' in rows[0]['qc_issues']


def test_sma_projection_endpoint_without_trajectory():
    from src.positional import sma_projected_metric
    mesh=pv.Cube(bounds=(-10,10,-10,10,-10,10)).triangulate()
    markers=dict(subject='synthetic',fiducials=[dict(name='confirmed-cap',position=[0,0,12])])
    targets=[dict(name='SMA',position=[3,4,12],position_source=[3,4,12]),dict(name='SMA Skin',position=[9,9,9])]
    review=dict(source_mri_sha256='a'*64,marker_mri_sha256='b'*64,
                mappings=dict(SMA=dict(marker='confirmed-cap',brainsight='SMA',confirmed=True,evidence='explicit user confirmation')))
    reg=dict(source_sha256='a'*64,target_sha256='b'*64,numerical_qc='passed',verified=True)
    surface=dict(verified=True,surface_sha256='c'*64)
    r=sma_projected_metric(mesh,markers,targets,review,reg,surface)
    assert r['distance_mm']==pytest.approx(5)
    assert r['qc']=='verified' and r['brainsight_name']=='SMA'
    assert sma_projected_metric(mesh,markers,targets[:1],review,reg,surface)['distance_mm']==pytest.approx(5)
    accepted=dict(surface,review=dict(scope='user_visual_qc_acceptance'))
    assert sma_projected_metric(mesh,markers,targets,review,reg,accepted)['qc']=='reviewed'
    assert r['eeg_projection_offset_mm']==2 and r['brainsight_projection_offset_mm']==2
    assert r['eeg_raw']==[0,0,12] and r['brainsight_raw_cap']==[3,4,12]
    assert sma_projected_metric(mesh,markers,targets,review,reg,dict(surface,verified=False))['qc']=='provisional'
    review['mappings']['SMA']['confirmed']=False
    assert sma_projected_metric(mesh,markers,targets,review,reg,surface)['qc']=='unavailable'


def test_independent_triangle_projection_and_competing_regions():
    from src.projection_audit import independent_project
    mesh=pv.PolyData([[0.,0,0],[10,0,0],[0,10,0]],[3,0,1,2])
    q=independent_project(mesh,[2,3,4]);assert np.allclose(q['position'],[2,3,0]);assert q['distance_mm']==4
    q=independent_project(mesh,[-3,0,4]);assert np.allclose(q['position'],[0,0,0]);assert q['distance_mm']==5
    cube=pv.Cube(bounds=(-10,10,-10,10,-10,10)).triangulate()
    ambiguous=independent_project(cube,[0,0,0])
    assert ambiguous['competing_region']['distance_gap_mm']==pytest.approx(0)
