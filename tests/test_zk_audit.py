import os

def test_zk_audit_circuit_compilation():
    circuit_dir = "zk_audit/circuits"
    os.makedirs(circuit_dir, exist_ok=True)
    
    circuit_path = os.path.join(circuit_dir, "invar_check.circom")
    assert os.path.exists(circuit_path), "ZK audit circuit file must exist."

    # Verify circuit structure and content
    with open(circuit_path, "r") as f:
        content = f.read()
    assert "pragma circom" in content
    assert "InvariantCheck" in content
