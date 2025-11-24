from datetime import datetime, timezone
import json

def now():
    return datetime.now(timezone.utc).isoformat()

class AuditTrail:
    def __init__(self):
        self.logs = []

    def log(self, stage, action, details):
        self.logs.append({
            "timestamp": now(),
            "stage": stage,
            "action": action,
            "details": details
        })

    def log_prediction(self, telemetry):
        self.log("prediction", "telemetry_read", telemetry)

    def log_overload(self, required_kw):
        self.log("prediction", "overload_detected", {
            "required_kw": required_kw
        })
    
    def log_escalation(self, reason):
        self.log("optimisation", "escalation_triggered", {"reason": reason})


    def log_discover_sent(self, message_id):
        self.log("dispatch", "discover_sent", {"message_id": message_id})

    def log_discover_received(self, count):
        self.log("dispatch", "discover_received", {"windows_found": count})

    def log_selection(self, selected, required_kw):
        self.log("optimisation", "der_selected", {
            "required_kw": required_kw,
            "selected": [
                {"id": w["id"], "capacity_kw": w["capacity_kw"], "region": w["region"]}
                for w in selected
            ]
        })

    def log_confirm_sent(self, order_id, selected):
        self.log("dispatch", "confirm_sent", {
            "order_id": order_id,
            "selected_ids": [w["id"] for w in selected]
        })

    def log_status_requested(self, order_id):
        self.log("dispatch", "status_requested", {"order_id": order_id})

    def print_audit(self):
        print("\n=== AUDIT TRAIL ===")
        for entry in self.logs:
            print(f"\n[{entry['timestamp']}]")
            print(f" Stage : {entry['stage']}")
            print(f" Action: {entry['action']}")
            print(f" Details:")
            print(json.dumps(entry["details"], indent=4))

    def dump_json(self, filename="audit_log.json"):
        with open(filename, "w") as f:
            json.dump(self.logs, f, indent=4)
        print(f"\n[AuditTrail] Saved audit log → {filename}")
