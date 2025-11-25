class EscalationChecker:
    """
    Runs safety, economic, and feasibility escalations.

    Warnings only trigger on majorities or critical issues.
    """

    def __init__(self, audit):
        self.audit = audit

    def run(self, windows):
        if not windows:
            self.audit.log_escalation("no_windows_found")
            return

        count = len(windows)

        reservation_required_count = sum(
            1 for w in windows if w.get("reservation_required")
        )
        if reservation_required_count >= max(2, count * 0.7):
            self.audit.log_escalation("majority_reservation_required")

        high_comfort_count = sum(
            1 for w in windows if (w.get("comfort_penalty") or 0) > 0.95
        )
        if high_comfort_count >= max(2, count * 0.5):
            self.audit.log_escalation("critical_comfort_risk")

        volatile_count = sum(
            1 for w in windows if w.get("price_stability") == "volatile"
        )
        if volatile_count >= max(3, count * 0.5):
            self.audit.log_escalation("widespread_price_volatility")

        slow_count = sum(
            1 for w in windows if (w.get("response_time_s") or 0) > 20
        )
        if slow_count >= max(2, count * 0.5):
            self.audit.log_escalation("slow_der_cluster_detected")

        if any((w.get("response_time_s") or 0) > 60 for w in windows):
            self.audit.log_escalation("unusable_der_detected")
