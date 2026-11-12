import numpy as np
from src.emvelop_rf import RFConfig,transfer,sources,basis,optimize

def test_quadrature_and_transverse_far_field():
    c=RFConfig(); p=np.array([[0,0,0],[.02,.01,.03]])
    g=transfer(p,sources(c)[0],c)
    c.quadrature=16
    np.testing.assert_allclose(g,transfer(p,sources(c)[0],c),rtol=1e-7,atol=1e-8)
    # On dipole equatorial plane there is no x or y component.
    eq=transfer(np.array([[0,0,0]]),np.array([[.085,0,0]]),c)
    assert np.linalg.norm(eq[0,:2])<1e-12

def test_target_nullspace_and_complex_gradient():
    c=RFConfig(); s=sources(c)
    t=[transfer(np.zeros((1,3)),a,c)[0] for a in s]
    w,z=basis(t[0]); np.testing.assert_allclose(t[0]@w,[0,0,.5],atol=1e-12)
    np.testing.assert_allclose(t[0]@z,0,atol=1e-12)
    rng=np.random.default_rng(2); p=rng.uniform(-.03,.03,(30,3))
    g=[transfer(p,a,c) for a in s]
    initial,final,trials,fun=optimize(*g,*t,seeds=1)
    x=rng.normal(size=36)*.001; f,grad=fun(x)
    for j in [0,7,19,35]:
        dx=np.zeros(36);dx[j]=1e-7
        numerical=(fun(x+dx)[0]-fun(x-dx)[0])/2e-7
        np.testing.assert_allclose(grad[j],numerical,rtol=2e-4,atol=1e-5)
    assert trials[0]['objective']<=fun(np.zeros(36))[0]+1e-10

def test_green_far_field_radiative_asymptote():
    from src.emvelop_rf import MU0, EPS0
    c=RFConfig(conductivity=0., length=1e-5)
    omega=2*np.pi*c.frequency
    k=omega*np.sqrt(MU0*EPS0*c.epsilon_r)
    distance=20.
    actual=transfer(np.array([[distance,0.,0.]]),np.zeros((1,3)),c)[0,:,0]
    expected=-1j*omega*MU0*c.length*np.exp(-1j*k*distance)/(4*np.pi*distance)
    np.testing.assert_allclose(actual[2],expected,rtol=3e-4)
    assert np.linalg.norm(actual[:2])<1e-14

def test_source_free_maxwell_residual():
    from src.emvelop_rf import MU0, EPS0
    c=RFConfig(); source=np.array([[.085,.012,-.01]])
    p=np.array([.013,-.018,.024]); h=1e-5
    def e(x): return transfer(x[None,:],source,c)[0,:,0]
    center=e(p); lap=np.zeros(3,complex); graddiv=np.zeros(3,complex)
    for j in range(3):
        d=np.eye(3)[j]*h
        lap+=(e(p+d)-2*center+e(p-d))/h**2
        for i in range(3):
            a=np.eye(3)[i]*h
            graddiv[i]+=(e(p+a+d)[j]-e(p+a-d)[j]-e(p-a+d)[j]+e(p-a-d)[j])/(4*h*h)
    omega=2*np.pi*c.frequency
    k2=omega**2*MU0*EPS0*c.epsilon_r-1j*omega*MU0*c.conductivity
    residual=graddiv-lap-k2*center
    assert np.linalg.norm(residual)/np.linalg.norm(k2*center)<1e-4
