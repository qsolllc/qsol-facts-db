import json
import datetime

class ComplianceReporter:
    def __init__(self, client_name: str, tier: str = "Standard"):
        self.client_name = client_name
        self.tier = tier
        # Resolved deprecation by using timezone-aware UTC datetime.now(datetime.UTC)
        self.timestamp = datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")

    def generate_audit_report(self, verified_logs_count: int, blocked_logs_count: int) -> dict:
        """Generate a standardized enterprise compliance onboarding dossier."""
        total_requests = verified_logs_count + blocked_logs_count
        compliance_rate = (verified_logs_count / total_requests * 100) if total_requests > 0 else 100.0

        report = {
            "client": self.client_name,
            "service_tier": self.tier,
            "timestamp": self.timestamp,
            "telemetry_standard": "333",
            "metrics": {
                "total_processed": total_requests,
                "verified_passes": verified_logs_count,
                "security_blocks": blocked_logs_count,
                "compliance_score_percent": round(compliance_rate, 2)
            },
            "status": "APPROVED" if compliance_rate >= 80.0 else "REVIEW_REQUIRED"
        }
        return report
