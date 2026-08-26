import pytest
import json
from facts_db.guard import TelemetryGuard, SecurityError

def test_telemetry_guard_success():
    guard = TelemetryGuard(required_invariant="333")
    valid_payload = json.dumps({"state": "ACTIVE", "component": "telemetry_node"})
    
    secured_packet_str = guard.intercept_and_validate(
        valid_payload, 
        "state == ACTIVE & (component == telemetry_node | fallback)"
    )
    
    packet = json.loads(secured_packet_str)
    assert packet["telemetry_standard"] == "333"
    assert packet["payload"]["state"] == "ACTIVE"

def test_telemetry_guard_rejection():
    guard = TelemetryGuard(required_invariant="333")
    invalid_payload = json.dumps({"state": "DOWN", "component": "telemetry_node"})
    
    # Should fail because state is not ACTIVE
    with pytest.raises(SecurityError):
        guard.intercept_and_validate(
            invalid_payload, 
            "state == ACTIVE & component == telemetry_node"
        )
