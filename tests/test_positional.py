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
    mappings={s:dict(marker='cap',brainsight='planned') for s in ['SMA','right_DLPFC']}
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
