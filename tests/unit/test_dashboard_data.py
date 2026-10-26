import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

pytestmark = pytest.mark.unit

spec=importlib.util.spec_from_file_location('dashboard_data',Path(__file__).resolve().parents[2]/'Dashboard/webapp/data_loader.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def test_business_values_and_percentage_are_not_fabricated():
    df=pd.DataFrame({'monetary':[25.,1800.], 'frequency':[2,9], 'recency':[0,30], 'churn_risk_pct':[.5,50.], 'churn_probability':[.005,.5]})
    expected=df.copy();module.SupabaseRepository._normalize(df)
    pd.testing.assert_frame_equal(df.drop(columns='churn_probability'),expected.drop(columns='churn_probability'))
    assert df.churn_probability.tolist()==[.5,50.]

def test_invalid_source_probability_is_rejected():
    with pytest.raises(ValueError,match='probability'):module.SupabaseRepository._normalize(pd.DataFrame({'churn_probability':[20.]}))

def test_missing_configuration_uses_explicit_demo(monkeypatch):
    def reject_network(*args):raise AssertionError('Network must not be called without credentials')
    monkeypatch.setattr(module,'create_client',reject_network)
    assert module.SupabaseRepository('','').connect()._demo_mode

def test_configured_connection_receives_credentials(monkeypatch):
    calls=[]
    monkeypatch.setattr(module,'create_client',lambda url,key:calls.append((url,key)) or object())
    repo=module.SupabaseRepository('https://example.invalid','test-key').connect()
    assert not repo._demo_mode and calls==[('https://example.invalid','test-key')]

def test_demo_is_deterministic_without_changing_global_rng():
    before=np.random.get_state();first=module._generate_demo_data();after=np.random.get_state()
    assert np.array_equal(before[1],after[1]) and before[2:]==after[2:]
    for a,b in zip(first,module._generate_demo_data()):pd.testing.assert_frame_equal(a,b)
