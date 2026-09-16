from datetime import datetime, timezone

def build_report(ref, search_result):
    found_count = search_result.get("count", 0)
    records = search_result.get("results", [])
    
    report = {
        "transaction_ref": ref,
        "found": found_count,
        "transactions": []
    }
    
    for tx in records:
        anomalies = []
        status = tx.get("status")
        created_at_str = tx.get("created_at")
        callbacks = tx.get("callbacks", [])
        
        # 1. Check for Stuck Processing Status
        if status == "PROCESSING" and created_at_str:
            try:
                # Handle varying ISO string structures safely
                clean_time = created_at_str.replace("Z", "+00:00")
                created_dt = datetime.fromisoformat(clean_time)
                if created_dt.tzinfo is None:
                    created_dt = created_dt.replace(tzinfo=timezone.utc)
                
                # Check absolute operational threshold age
                age_seconds = (datetime.now(timezone.utc) - created_dt).total_seconds()
                if age_seconds > 900:  # 15 minutes
                    anomalies.append("Transaction stuck in PROCESSING for over 15 minutes")
            except Exception:
                pass
        
        # 2. Check for Missing Callbacks on Failures
        if status == "FAILED" and len(callbacks) == 0:
            anomalies.append("Failed transaction has no callback attempts recorded")
            
        # 3. Check for Total Callback Failure Cascades
        if len(callbacks) > 0 and all(c.get("callback_status") == "FAILED" for c in callbacks):
            anomalies.append("All callback attempts failed — merchant not notified")
            
        # 4. Check for Global Data Duplication Identifiers
        if found_count > 1:
            anomalies.append(f"Duplicate transaction_ref detected — {found_count} rows share this reference")
            
        # Determine likely internal cause
        if status == "PROCESSING":
            likely_cause = "Payment not yet processed or stuck in queue"
        elif status == "FAILED":
            likely_cause = tx.get("failure_code") or "Unknown failure — check callback logs"
        else:
            likely_cause = None
            
        # Determine recommended recovery actions
        if status == "PROCESSING" and any("stuck" in a for a in anomalies):
            recommended_action = "Escalate to payments team — transaction may be stuck"
        elif status == "FAILED":
            recommended_action = "Retry the payment or contact the customer"
        else:
            recommended_action = "No action required."
            
        report["transactions"].append({
            "id": tx.get("id"),
            "status": status,
            "amount": tx.get("amount"),
            "customer_id": tx.get("customer_id"),
            "created_at": created_at_str,
            "completed_at": tx.get("completed_at"),
            "failure_code": tx.get("failure_code"),
            "callbacks": callbacks,
            "anomalies": anomalies,
            "likely_cause": likely_cause,
            "recommended_action": recommended_action
        })
        
    return report
