import argparse
import json
import sys
import logging
from python.config import Config
from python.client import MiniPayClient
from python.diagnostics import build_report

def main():
    parser = argparse.ArgumentParser(description="MiniPay L2 support tool")
    parser.add_argument("--transaction", metavar="REF", help="transaction_ref to diagnose")
    parser.add_argument("--health", action="store_true", help="check API health")
    parser.add_argument("--json", action="store_true", dest="as_json", help="output as JSON")
    parser.add_argument("--config", metavar="PATH", help="path to JSON config file")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING)

    config = Config(config_file=args.config)
    client = MiniPayClient(config)

    # 1. Process System Health Queries
    if args.health:
        try:
            health_data = client.get_health()
            if args.as_json:
                print(json.dumps(health_data, indent=2))
            else:
                print(f"System Health: {health_data.get('status', 'UNKNOWN').upper()}")
                print(f"Database Node: {health_data.get('database', 'UNKNOWN').upper()}")
            sys.exit(0)
        except Exception as e:
            if args.as_json:
                print(json.dumps({"error": "Unhealthy", "detail": str(e)}))
            else:
                print(f"CRITICAL: API Health Verification Fault -> {e}", file=sys.stderr)
            sys.exit(2)

    # 2. Process Transaction Diagnoses Queries
    if args.transaction:
        try:
            search_data = client.search_transaction(args.transaction)
            report = build_report(args.transaction, search_data)
            
            if args.as_json:
                print(json.dumps(report, indent=2))
                # Return code 1 if any generated record holds active anomalies
                has_anomalies = any(len(t["anomalies"]) > 0 for t in report["transactions"])
                sys.exit(1 if has_anomalies else 0)
            else:
                print(f"Transaction Reference: {report['transaction_ref']}")
                print(f"Found: {report['found']} record(s)\n")
                
                if report['found'] == 0:
                    print("No matching record balances located.")
                    sys.exit(2)
                    
                has_anomalies = False
                for idx, tx in enumerate(report["transactions"], 1):
                    print(f"--- Record {idx} ---")
                    print(f"ID:          {tx['id']}")
                    print(f"Status:      {tx['status']}")
                    print(f"Amount:      {tx['amount']}")
                    print(f"Customer ID: {tx['customer_id']}")
                    print(f"Created:     {tx['created_at']}")
                    print(f"Completed:   {tx['completed_at']}")
                    
                    cb_count = len(tx['callbacks'])
                    last_status = tx['callbacks'][-1].get('callback_status', 'NONE') if cb_count > 0 else 'NONE'
                    print(f"Callbacks:   {cb_count} attempt(s), last status: {last_status}")
                    
                    anom_list = ", ".join(tx['anomalies']) if len(tx['anomalies']) > 0 else "None"
                    print(f"Anomalies:   {anom_list}")
                    print(f"Action:      {tx['recommended_action']}\n")
                    if len(tx['anomalies']) > 0:
                        has_anomalies = True
                        
                sys.exit(1 if has_anomalies else 0)
        except Exception as e:
            print(f"ERROR: Execution Fault -> {e}", file=sys.stderr)
            sys.exit(2)

    if not args.health and not args.transaction:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
