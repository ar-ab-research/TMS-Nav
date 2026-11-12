import numpy as np
import pytest
from src.emvelop_thermal import steady_temperature

def test_uniform_heating_exact_equilibrium():
    p=np.stack(np.meshgrid(*([np.arange(4)*.01]*3),indexing='ij'),axis=-1).reshape(-1,3)
    t,qc=steady_temperature(p,np.full(len(p),5000.),.01)
    np.testing.assert_allclose(t,.5,atol=1e-10)
    assert qc['energy_balance_relative']<1e-10

def test_energy_conservation_positive_and_scaling():
    p=np.stack(np.meshgrid(*([np.arange(4)*.01]*3),indexing='ij'),axis=-1).reshape(-1,3)
    q=np.zeros(len(p)); q[21]=10000
    t,qc=steady_temperature(p,q,.01)
    twice,_=steady_temperature(p,2*q,.01)
    assert t.min()>0
    np.testing.assert_allclose(twice,2*t,atol=1e-10)
    assert qc['relative_residual']<1e-8
    assert qc['energy_balance_relative']<1e-8

def test_invalid_perfusion():
    with pytest.raises(ValueError): steady_temperature(np.zeros((1,3)),np.ones(1),.01,perfusion_sink=0)
