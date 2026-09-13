import json
import hashlib
import os

def verify_kernel():
    base_dir = "/data/data/com.termux/files/home/capctl"
    kernel_path = os.path.join(base_dir, "QSOL_CORE_V1_KERNEL.json")
    attestation_path = os.path.join(base_dir, "EPOCH_0004_ATTESTATION.json")
    timestamp_path = os.path.join(base_dir, "EPOCH_0004_TIMESTAMP_REQUEST.json")
    
    with open(kernel_path, "r") as f:
        kernel = json.load(f)
        
    with open(attestation_path, "rb") as f:
        att_hash = hashlib.sha256(f.read()).hexdigest()
        
    with open(timestamp_path, "rb") as f:
        ts_hash = hashlib.sha256(f.read()).hexdigest()
        
    assert kernel["attestation_sha256"] == att_hash, "Attestation hash mismatch!"
    assert kernel["timestamp_request_sha256"] == ts_hash, "Timestamp request hash mismatch!"
    assert kernel["invariant"] == "333", "Trinitarian invariant violation!"
    
    print("QSOL-CORE-V1 cryptographic kernel verification: PASSED")

if __name__ == "__main__":
    verify_kernel()
