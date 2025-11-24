import itertools

class OptimisationAgent:
    def __init__(self, audit):
        self.audit = audit

    def select_der(self, windows, required_kw):
        if not windows:
            print("[OptimisationAgent] No DER windows available!")
            return []

        windows = self.prepare_windows(windows)
        windows = self.rank_windows(windows)

        single = self.pick_single(windows, required_kw)
        if single:
            self.audit.log_selection(single, required_kw)
            return single

        subset = self.knapsack_minimal_feasible(windows, required_kw)
        self.audit.log_selection(subset, required_kw)
        
        print("\n[OptimisationAgent] Selected DER set (knapsack):")
        print(f"  Total: {sum(w['capacity_kw'] for w in subset)} kW (needed {required_kw} kW)")
        for w in subset:
            print(f"   - {w['id']} | {w['capacity_kw']} kW | RE {w['renewable_mix']}%")
        

        return subset

    def prepare_windows(self, windows):
        for w in windows:
            w["capacity_kw"] = int((w.get("capacity_mw") or 0) * 1000)
        return windows

    def score(self, w):
        return (w.get("renewable_mix") or 0) * 2 - (w.get("carbon_intensity") or 999)

    def rank_windows(self, windows):
        ranked = sorted(windows, key=self.score, reverse=True)
        best = ranked[0]
        print("\n[OptimisationAgent] Highest-scoring DER overall:")
        print(f"   - {best['id']} | {best['capacity_kw']} kW | RE {best['renewable_mix']}%")
        return ranked

    def pick_single(self, windows, required_kw):
        for w in windows:
            if w["capacity_kw"] >= required_kw:
                print("\n[OptimisationAgent] Best single DER meets the requirement.")
                return [w]
        return None
    
    def knapsack_minimal_feasible(self, windows, required_kw):
        best_subset = None
        best_overshoot = float("inf")

        for r in range(1, len(windows) + 1):
            for subset in itertools.combinations(windows, r):
                total = sum(w["capacity_kw"] for w in subset)
                if total >= required_kw:
                    overshoot = total - required_kw
                    if overshoot < best_overshoot:
                        best_overshoot = overshoot
                        best_subset = subset

        if best_subset is None:
            print("[OptimisationAgent] No feasible combination — selecting all DERs.")
            return windows
        
        return list(best_subset)
