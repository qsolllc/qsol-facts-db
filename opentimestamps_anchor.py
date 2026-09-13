import hashlib
import urllib.request
import json
import sys

def create_anchor_payload(attestation_path):
    with open(attestation_path, 'rb') as f:
        file_bytes = f.read()
    
    digest = hashlib.sha256(file_bytes).hexdigest()
    print(f"ATTESTATION_SHA256: {digest}")
    
    payload = {
        "hash": digest,
        "engine": "OpenTimestamps-Calendar-Proxy",
        "node": "Pocatello-ARM64"
    }
    
    output_path = "/data/data/com.termux/files/home/capctl/EPOCH_0004_TIMESTAMP_REQUEST.json"
    with open(output_path, 'w') as f:
        json.dump(payload, f, indent=2)
        
    print(f"Timestamp submission payload generated: {output_path}")

if __name__ == "__main__":
    create_anchor_payload("/data/data/com.termux/files/home/capctl/EPOCH_0004_ATTESTATION.json")
