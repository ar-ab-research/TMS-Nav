import numpy as np
from src.emvelop_feasibility import Config,loop_a,fields,magnitude,sar

def test_axis_null_and_symmetry():
    c=Config(); a,b=fields(np.array([[0,0,0],[0,.03,0]]),c)
    assert np.linalg.norm(a[0])<1e-12
    np.testing.assert_allclose(a,b,atol=1e-12)
    assert magnitude(a,b,np.pi)[1]<1e-12

def test_quadrature_convergence_and_linearity():
    p=np.array([[.04,.03,.01]])
    np.testing.assert_allclose(loop_a(p,.1,.05,128),loop_a(p,.1,.05,256),rtol=1e-10,atol=1e-20)
    a,b=fields(p,Config()); aa,bb=fields(p,Config(peak_current=10000))
    np.testing.assert_allclose(aa,2*a); np.testing.assert_allclose(bb,2*b)

def test_heating_peak_rms_and_duty():
    c=Config()
    assert np.isclose(sar(100,c,duty=1),1)
    assert np.isclose(sar(100,c),.002)


def test_ti_relative_phase_changes_timing_only():
    # Analytic envelope of two collinear carriers over a full beat cycle.
    a,b=3.,5.
    theta=np.linspace(0,2*np.pi,100001)
    depths=[]
    for phase in (0.,.4,1.8):
        envelope=np.abs(a+b*np.exp(1j*(theta+phase)))
        depths.append(envelope.max()-envelope.min())
    np.testing.assert_allclose(depths,2*min(a,b),rtol=1e-8)
