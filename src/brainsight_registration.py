"""Rigid source MRI -> cap MRI registration. SimpleITK uses LPS/fixed->moving."""
import json
from pathlib import Path
import numpy as np
import SimpleITK as sitk
from src.subject_coordinates import RAS_LPS, apply_affine, file_hash, load_native, validate_matrix


def ras_source_to_cap(fixed_to_moving):
    origin=np.array(fixed_to_moving.TransformPoint((0.,0.,0.)))
    m=np.eye(4);m[:3,3]=origin
    m[:3,:3]=np.column_stack([np.array(fixed_to_moving.TransformPoint(tuple(v)))-origin for v in np.eye(3)])
    return validate_matrix(RAS_LPS @ np.linalg.inv(m) @ RAS_LPS)


def register(source, cap, output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    key=dict(source_sha256=file_hash(source),target_sha256=file_hash(cap),method='rigid_MattesMI_v1')
    cached=output/'registration.json'
    if cached.exists():
        data=json.loads(cached.read_text())
        if all(data.get(k)==v for k,v in key.items()):return data
    load_native(source);load_native(cap)
    sitk.ProcessObject.SetGlobalDefaultNumberOfThreads(1)
    moving=sitk.ReadImage(str(source),sitk.sitkFloat32);fixed=sitk.ReadImage(str(cap),sitk.sitkFloat32)
    initial=sitk.CenteredTransformInitializer(fixed,moving,sitk.Euler3DTransform(),sitk.CenteredTransformInitializerFilter.GEOMETRY)
    method=sitk.ImageRegistrationMethod();method.SetMetricAsMattesMutualInformation(50)
    method.SetMetricSamplingStrategy(method.RANDOM);method.SetMetricSamplingPercentage(.12,1729)
    method.SetInterpolator(sitk.sitkLinear)
    method.SetOptimizerAsRegularStepGradientDescent(learningRate=2.,minStep=.005,numberOfIterations=250)
    method.SetOptimizerScalesFromPhysicalShift();method.SetShrinkFactorsPerLevel([4,2,1])
    method.SetSmoothingSigmasPerLevel([2,1,0]);method.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()
    method.SetInitialTransform(initial,inPlace=False);result=method.Execute(fixed,moving)
    matrix=ras_source_to_cap(result)
    if not np.allclose(matrix[:3,:3].T@matrix[:3,:3],np.eye(3),atol=1e-5) or np.linalg.det(matrix[:3,:3])<0:
        raise ValueError('Registration is not a proper rigid rotation')
    probes=np.array([[0,0,0],[20,-30,40],[-30,20,60]],float)
    error=float(np.max(np.abs(apply_affine(np.linalg.inv(matrix),apply_affine(matrix,probes))-probes)))
    if error>1e-6 or not np.isfinite(method.GetMetricValue()):raise ValueError('Registration numerical QC failed')
    sitk.WriteTransform(result,str(output/'cap_to_source_LPS.tfm'))
    aligned=sitk.Resample(moving,fixed,result,sitk.sitkLinear,0.,sitk.sitkFloat32)
    sitk.WriteImage(aligned,str(output/'source_in_cap.nii.gz'))
    before=sitk.Resample(moving,fixed,sitk.Transform(3,sitk.sitkIdentity),sitk.sitkLinear,0.,sitk.sitkFloat32)
    qc_views(fixed,before,aligned,output/'registration-qc.png')
    data=dict(**key,axes='RAS',units='mm',direction='source_to_cap',matrix=matrix.tolist(),
              inverse_matrix=np.linalg.inv(matrix).tolist(),roundtrip_max_mm=error,determinant=float(np.linalg.det(matrix[:3,:3])),
              metric=float(method.GetMetricValue()),optimizer_stop=method.GetOptimizerStopConditionDescription(),
              numerical_qc='passed',anatomical_qc='review_required',verified=False,
              seed=1729,qc_image='registration-qc.png',resampling_transform='cap_to_source_LPS.tfm')
    cached.write_text(json.dumps(data,indent=2));return data


def qc_views(fixed,before,after,path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    f,b,a=[sitk.GetArrayFromImage(i) for i in (fixed,before,after)]
    def norm(v):
        values=v[v>0];hi=np.percentile(values,99) if len(values) else 1
        return np.clip(v/hi,0,1)
    f,b,a=map(norm,(f,b,a))
    fig,axes=plt.subplots(3,6,figsize=(16,8))
    for plane in range(3):
        axis=2-plane
        for col,fraction in enumerate((.35,.5,.65)):
            k=int(f.shape[axis]*fraction)
            fs=np.take(f,k,axis=axis);bs=np.take(b,k,axis=axis);aa=np.take(a,k,axis=axis)
            for offset,moving,title in ((0,bs,'Before'),(3,aa,'Registered')):
                rgb=np.stack([fs,moving,fs],axis=-1)
                axes[plane,col+offset].imshow(np.rot90(rgb),origin='lower')
                axes[plane,col+offset].set_title(f'{title}: axis {axis}, slice {k}',fontsize=8);axes[plane,col+offset].axis('off')
    fig.suptitle('Cap MRI = magenta; Brainsight MRI = green. White agreement; inspect brain, ventricles and contours. Native index slices.')
    fig.tight_layout();fig.savefig(path,dpi=140);plt.close(fig)
