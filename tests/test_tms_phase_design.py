import numpy as np
from src.tms_phase_design import Loop,loop_field,vector_peak,constrained_weights
from src.emvelop_feasibility import loop_a

def test_general_loop_matches_axis_aligned_quadrature():
    p=np.array([[.01,.02,.03],[0,0,0]])
    expected=loop_a(p,.1,.05,256)*2*np.pi*3000*1000
    np.testing.assert_allclose(loop_field(p,Loop((.1,0,0)),segments=256),expected,atol=1e-13)

def test_vector_peak_elliptical_not_phasor_norm():
    e=np.array([[1,1j,0],[2,1j,0]],complex)
    np.testing.assert_allclose(vector_peak(e),[1,2])
    time=np.linspace(0,2*np.pi,10001)
    direct=np.linalg.norm((e[:,None,:]*np.exp(1j*time)[None,:,None]).real,axis=-1).max(axis=1)
    np.testing.assert_allclose(vector_peak(e),direct,atol=1e-7)

def test_complex_quadratic_optimum_and_constraint():
    rng=np.random.default_rng(17); g=rng.normal(size=(20,3,2))+1j*rng.normal(size=(20,3,2))
    h=np.array([1+.3j,.4-.8j]); w,q=constrained_weights(g,h,.01)
    np.testing.assert_allclose(h@w,1,atol=1e-12)
    null=np.array([h[1],-h[0]])
    base=np.vdot(w,q@w).real
    for alpha in [.1,1j,-.2+.3j]:
        v=w+alpha*null
        assert np.vdot(v,q@v).real>base

def test_loop_rotation_covariance():
    p=np.array([[.01,.02,.03]])
    rot=np.array([[0,-1,0],[1,0,0],[0,0,1]])
    a=loop_field(p,Loop((.1,0,0)))
    b=loop_field(p@rot.T,Loop((0,.1,0),(0,1,0)))
    np.testing.assert_allclose(b,a@rot.T,atol=1e-12)
