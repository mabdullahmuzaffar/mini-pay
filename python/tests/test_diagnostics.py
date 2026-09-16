from python.diagnostics import build_report

def _make_result(status="SUCCESS", count=1, callbacks=None):
    return {
        "count": count,
        "results": [{
            "id": 1,
            "transaction_ref": "TXN001",
            "customer_id": 10,
            "amount": "100.00",
            "status": status,
            "created_at": "2026-09-16T00:00:00Z",
            "completed_at": "2026-09-16T00:01:00Z",
            "failure_code": None,
            "callbacks": callbacks or []
        }]
    }

def test_no_anomalies_for_success():
    result = _make_result(status="SUCCESS")
    report = build_report("TXN001", result)
    assert report["transactions"][0]["anomalies"] == []

def test_stuck_processing_flagged():
    # Force a transaction older than 15 minutes using an explicitly old creation date stamp
    res = _make_result(status="PROCESSING")
    res["results"][0]["created_at"] = "2026-09-01T00:00:00Z"
    report = build_report("TXN001", res)
    assert any("stuck" in a for a in report["transactions"][0]["anomalies"])
