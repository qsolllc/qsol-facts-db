import hashlib

class TrustMatrix:
    def __init__(self, trustees: list[str], threshold: int = 2):
        self.trustees = trustees
        self.threshold = threshold

    def _sign_share(self, trustee: str, state_hash: str) -> str:
        """Simulate a cryptographic signature share from a specific trustee."""
        payload = f"{trustee}:{state_hash}"
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    def authorize_recovery(self, state_hash: str, approvals: dict[str, str]) -> bool:
        """
        Verify that a quorum of valid signatures from designated trustees 
        meets or exceeds the required threshold.
        """
        valid_shares = 0
        for trustee, sig in approvals.items():
            if trustee in self.trustees:
                expected_sig = self._sign_share(trustee, state_hash)
                if sig == expected_sig:
                    valid_shares += 1
                    
        return valid_shares >= self.threshold
