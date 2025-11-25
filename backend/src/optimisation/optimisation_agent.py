from .scorer import DERScorer
from .prep import WindowPreprocessor
from .escalations import EscalationChecker
from .knapsack import KnapsackSolver


class OptimisationAgent:
    """
    Chooses DER flexibility windows and decides mode:

      - incentive  -> normal demand-response, incentive is paid
      - emergency  -> urgent curtailment, prioritise speed/reliability

    select_der returns (selected_windows, mode, meta)
    """

    def __init__(self, audit, emergency_threshold_kw=4000):
        self.audit = audit
        self.scorer = DERScorer()
        self.prep = WindowPreprocessor()
        self.escalations = EscalationChecker(audit)
        self.knapsack = KnapsackSolver()
        self.emergency_threshold_kw = emergency_threshold_kw

    # Remove incentive payments entirely for emergency responses
    def strip_payments(self, windows):
        """Remove incentives for all DERs in emergency mode."""
        for w in windows:
            w["price_kw"] = 0
            w["price_currency"] = None
            w["incentive_paid"] = False
        return windows


    def select_der(self, windows, required_kw):
        """Return (selected_windows, mode, meta_dict)."""

        # Check for upstream escalation reasons
        self.escalations.run(windows)

        # Decide operating mode
        mode = "emergency" if required_kw >= self.emergency_threshold_kw else "incentive"
        self.audit.log_escalation(f"mode_selected:{mode}")
        print(f"\n[OptimisationAgent] Mode selected -> {mode.upper()}")

        # No windows at all
        if not windows:
            meta = {
                "mode": mode,
                "required_kw": required_kw,
                "total_available_kw": 0,
                "total_selected_kw": 0,
                "shortfall_kw": required_kw,
                "incentives_paid": False,
            }
            self.audit.log_escalation("no_windows_found")
            self.audit.log_selection([], required_kw)
            return [], mode, meta

        # Clean & normalise data
        windows = self.prep.prepare(windows)

        # Sort based on mode
        if mode == "emergency":
            # Fastest DERs first
            windows = sorted(
                windows,
                key=lambda w: (w.get("response_time_s") or 999)
            )
        else:
            # Composite green/comfort/price ranking
            windows = self.scorer.rank(windows)

        # Try to satisfy requirement with a single DER
        single = self.pick_single(windows, required_kw)
        total_cap = sum(w["capacity_kw"] for w in windows)

        if single:
            print("\n[OptimisationAgent] Using single DER solution.")

            # Emergency mode → no payments
            if mode == "emergency":
                single = self.strip_payments(single)

            self.audit.log_selection(single, required_kw)
            meta = {
                "mode": mode,
                "required_kw": required_kw,
                "total_available_kw": total_cap,
                "total_selected_kw": sum(w["capacity_kw"] for w in single),
                "shortfall_kw": max(0, required_kw - sum(w["capacity_kw"] for w in single)),
                "incentives_paid": (mode != "emergency"),
            }
            return single, mode, meta

        # Not enough total capacity
        if total_cap < required_kw:
            print("\n[OptimisationAgent] Insufficient total capacity.")
            self.audit.log_escalation("insufficient_total_capacity")

            if mode == "emergency":
                windows = self.strip_payments(windows)

            self.audit.log_selection(windows, required_kw)

            meta = {
                "mode": mode,
                "required_kw": required_kw,
                "total_available_kw": total_cap,
                "total_selected_kw": total_cap,
                "shortfall_kw": required_kw - total_cap,
                "incentives_paid": (mode != "emergency"),
            }
            return windows, mode, meta

        # Use knapsack solver for subset selection
        subset = self.knapsack.solve(windows, required_kw)

        if mode == "emergency":
            subset = self.strip_payments(subset)

        self.audit.log_selection(subset, required_kw)
        self.print_selected(subset, required_kw)

        meta = {
            "mode": mode,
            "required_kw": required_kw,
            "total_available_kw": total_cap,
            "total_selected_kw": sum(w["capacity_kw"] for w in subset),
            "shortfall_kw": max(0, required_kw - sum(w["capacity_kw"] for w in subset)),
            "incentives_paid": (mode != "emergency"),
        }
        return subset, mode, meta

    def pick_single(self, windows, required_kw):
        """Choose a single DER that meets the requirement (best case)."""
        for w in windows:
            if w["capacity_kw"] >= required_kw:
                print("[OptimisationAgent] Best single DER meets requirement.")
                return [w]
        return None

    def print_selected(self, subset, required_kw):
        print("\n[OptimisationAgent] Selected DER set (knapsack):")
        total = sum(w["capacity_kw"] for w in subset)
        print(f"  Total = {total} kW | Needed = {required_kw}")
        for w in subset:
            print(
                f"   - {w['id']} | {w['capacity_kw']} kW | RE {w['renewable_mix']}%"
            )
