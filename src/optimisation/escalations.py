class EscalationChecker:
    """Runs safety, economic, and feasibility escalations."""

    def __init__(self, audit):
        self.audit = audit

    def run(self, windows):
        if not windows:
            self.audit.log_escalation("no_windows_found")
            return

        if all(w.get("reservation_required") for w in windows):
            self.audit.log_escalation("all_reservation_required")

        if any((w.get("comfort_penalty") or 0) > 0.8 for w in windows):
            self.audit.log_escalation("high_comfort_penalty_detected")

        if any(w.get("price_stability") == "volatile" for w in windows):
            self.audit.log_escalation("price_instability_detected")

        if any((w.get("response_time_s") or 99) > 8 for w in windows):
            self.audit.log_escalation("slow_der_response_time")
