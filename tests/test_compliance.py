from facts_db.compliance import ComplianceReporter

def test_compliance_reporter_generation():
    reporter = ComplianceReporter(client_name="Acme Corp", tier="Enterprise")
    report = reporter.generate_audit_report(verified_logs_count=95, blocked_logs_count=5)
    
    assert report["client"] == "Acme Corp"
    assert report["service_tier"] == "Enterprise"
    assert report["metrics"]["compliance_score_percent"] == 95.0
    assert report["status"] == "APPROVED"

def test_compliance_reporter_review_required():
    reporter = ComplianceReporter(client_name="Beta Corp", tier="Standard")
    report = reporter.generate_audit_report(verified_logs_count=50, blocked_logs_count=50)
    
    assert report["metrics"]["compliance_score_percent"] == 50.0
    assert report["status"] == "REVIEW_REQUIRED"
