from facts_db.telemetry import TelemetryVerifier
from facts_db.policy import PolicyEvaluator

def test_telemetry_verifier():
    verifier = TelemetryVerifier(standard_invariant="333")
    payload = '{"state": "ACTIVE", "node": "arm64"}'
    res = verifier.verify_payload(payload, "state == ACTIVE & (role == admin | override)")
    assert res["status"] == "APPROVED"
    assert res["standard"] == "333"

def test_policy_optimization_and_equivalence():
    policy = PolicyEvaluator()
    optimized = policy.optimize_policy("admin & (admin | guest)")
    assert optimized == "admin"

    assert policy.compare_policies("b & a", "a & b")
    assert not policy.compare_policies("admin", "guest")
