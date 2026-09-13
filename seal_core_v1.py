import json
import hashlib
import os

def seal_evidence_kernel():
    base_dir = "/data/data/com.termux/files/home/capctl"
    attestation_path = os.path.join(base_dir, "EPOCH_0004_ATTESTATION.json")
    timestamp_path = os.path.join(base_dir, "EPOCH_0004_TIMESTAMP_REQUEST.json")
    
    with open(attestation_path, "rb") as f:
        att_hash = hashlib.sha256(f.read()).hexdigest()
        
    with open(timestamp_path, "rb") as f:
        ts_hash = hashlib.sha256(f.read()).hexdigest()
        
    kernel_manifest = {
        "kernel": "QSOL-CORE-V1",
        "node": "Pocatello-ARM64",
        "attestation_sha256": att_hash,
        "timestamp_request_sha256": ts_hash,
        "status": "SEALED",
        "invariant": "333"
    }
    
    kernel_path = os.path.join(base_dir, "QSOL_CORE_V1_KERNEL.json")
    with open(kernel_path, "w") as f:
        json.dump(kernel_manifest, f, indent=2)
        
    print(f"QSOL-CORE-V1 evidence kernel sealed: {kernel_path}")

if __name__ == "__main__":
    seal_evidence_kernel()
