import json
from facts_db.core import FactsDB
from facts_db.telemetry import TelemetryVerifier

py_db = FactsDB()

class TelemetryGuard:
    def __init__(self, required_invariant: str = "333"):
        self.verifier = TelemetryVerifier(standard_invariant=required_invariant)
        self.db = FactsDB()

    def intercept_and_validate(self, raw_log_json: str, rule_invariant: str) -> str:
        """
        Intercepts incoming telemetry payloads, verifies length/depth safety boundaries,
        evaluates formal state invariants, and returns a verified, deterministically 
        serialized log packet adhering to standard 333.
        """
        # 1. Enforce strict byte-length and size safety limits
        if len(raw_log_json.encode('utf-8')) > self.db.max_len:
            raise ValueError(f"Telemetry payload rejected: exceeds max length of {self.db.max_len}")

        # 2. Run telemetry verification pass
        verification_result = self.verifier.verify_payload(raw_log_json, rule_invariant)
        
        if verification_result["status"] != "APPROVED":
            raise SecurityError(f"Invariant validation failed: {verification_result.get('reason')}")

        # 3. Deterministic serialization bound to standard 333
        parsed_payload = json.loads(raw_log_json)
        secured_packet = {
            "telemetry_standard": "333",
            "invariant_assertion": verification_result["invariant"],
            "payload": parsed_payload
        }
        
        return json.dumps(secured_packet, sort_keys=True)

class SecurityError(Exception):
    pass
