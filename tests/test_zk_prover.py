import os
import json
from zk_audit.prove import generate_witness_input, run_zk_audit_pipeline

def test_zk_prover_witness_generation():
    # Verify witness generation matches Standard 333 invariant constraints
    witness = generate_witness_input(private_state=350, public_threshold=333)
    assert witness["private_state"] >= witness["public_threshold"]
    assert witness["public_threshold"] == 333

def test_zk_pipeline_execution(tmp_path):
    # Test that the pipeline successfully serializes input JSON for the backend
    input_path = run_zk_audit_pipeline()
    assert os.path.exists(input_path)
    
    with open(input_path, "r") as f:
        data = json.load(f)
    assert data["private_state"] == 350
    assert data["public_threshold"] == 333
