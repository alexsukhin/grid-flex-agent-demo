from .scorer import DERScorer
from .prep import WindowPreprocessor
from .escalations import EscalationChecker
from .knapsack import KnapsackSolver


class OptimisationAgent:
    """
    Chooses DER flexibility windows and decides mode:

      - incentive  -> normal demand-response, incentive is paid
      - emergency  -> urgent curtailment, prioritise speed/reliability

    select_der now returns (selected_windows, mode, meta)
    """

    def __init__(self, audit, emergency_threshold_kw=5000):
        self.audit = audit
        self.scorer = DERScorer()
        self.prep = WindowPreprocessor()
        self.escalations = EscalationChecker(audit)
        self.knapsack = KnapsackSolver()
        self.emergency_threshold_kw = emergency_threshold_kw

    def select_der(self, windows, required_kw):
        """Return (selected_windows, mode, meta_dict)."""

        self.escalations.run(windows)

        mode = "emergency" if required_kw >= self.emergency_threshold_kw else "incentive"
        self.audit.log_escalation(f"mode_selected:{mode}")
        print(f"\n[OptimisationAgent] Mode selected -> {mode.upper()}")

        if not windows:
            meta = {
                "mode": mode,
                "required_kw": required_kw,
                "total_available_kw": 0,
                "total_selected_kw": 0,
                "shortfall_kw": required_kw,
            }
            self.audit.log_escalation("no_windows_found")
            self.audit.log_selection([], required_kw)
            return [], mode, meta

        windows = self.prep.prepare(windows)

        if mode == "emergency":
            # fastest first in emergency
            windows = sorted(
                windows,
                key=lambda w: (w.get("response_time_s") or 999)
            )
        else:
            # composite score (green + comfort + price + availability)
            windows = self.scorer.rank(windows)

        single = self.pick_single(windows, required_kw)
        total_cap = sum(w["capacity_kw"] for w in windows)

        if single:
            self.audit.log_selection(single, required_kw)
            meta = {
                "mode": mode,
                "required_kw": required_kw,
                "total_available_kw": total_cap,
                "total_selected_kw": sum(w["capacity_kw"] for w in single),
                "shortfall_kw": max(0, required_kw - sum(w["capacity_kw"] for w in single)),
            }
            return single, mode, meta

        if total_cap < required_kw:
            self.audit.log_escalation("insufficient_total_capacity")
            self.audit.log_selection(windows, required_kw)

            meta = {
                "mode": mode,
                "required_kw": required_kw,
                "total_available_kw": total_cap,
                "total_selected_kw": total_cap,
                "shortfall_kw": required_kw - total_cap,
            }
            return windows, mode, meta

        subset = self.knapsack.solve(windows, required_kw)
        self.audit.log_selection(subset, required_kw)
        self.print_selected(subset, required_kw)

        meta = {
            "mode": mode,
            "required_kw": required_kw,
            "total_available_kw": total_cap,
            "total_selected_kw": sum(w["capacity_kw"] for w in subset),
            "shortfall_kw": max(0, required_kw - sum(w["capacity_kw"] for w in subset)),
        }
        return subset, mode, meta

    def pick_single(self, windows, required_kw):
        for w in windows:
            if w["capacity_kw"] >= required_kw:
                print("\n[OptimisationAgent] Best single DER meets requirement.")
                return [w]
        return None

    def print_selected(self, subset, required_kw):
        print("\n[OptimisationAgent] Selected DER set (knapsack):")
        total = sum(w["capacity_kw"] for w in subset)
        print(f"  Total = {total} kW | Needed = {required_kw}")
        for w in subset:
            print(f"   - {w['id']} | {w['capacity_kw']} kW | RE {w['renewable_mix']}%")
