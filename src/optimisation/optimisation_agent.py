from .scorer import DERScorer
from .prep import WindowPreprocessor
from .escalations import EscalationChecker
from .knapsack import KnapsackSolver


class OptimisationAgent:
    def __init__(self, audit):
        self.audit = audit
        self.scorer = DERScorer()
        self.prep = WindowPreprocessor()
        self.escalations = EscalationChecker(audit)
        self.knapsack = KnapsackSolver()

    def select_der(self, windows, required_kw):
        self.escalations.run(windows)

        if not windows:
            return []

        windows = self.prep.prepare(windows)

        windows = self.scorer.rank(windows)

        single = self.pick_single(windows, required_kw)
        if single:
            self.audit.log_selection(single, required_kw)
            return single

        total_cap = sum(w["capacity_kw"] for w in windows)
        if total_cap < required_kw:
            self.audit.log_escalation("insufficient_total_capacity")
            self.audit.log_selection(windows, required_kw)
            return windows

        subset = self.knapsack.solve(windows, required_kw)
        self.audit.log_selection(subset, required_kw)

        self.print_selected(subset, required_kw)
        return subset

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
