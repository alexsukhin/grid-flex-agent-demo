import itertools

class OptimisationAgent:

    def select_der(self, windows, required_kw):
        if not windows:
            print("[OptimisationAgent] No DER windows available!")
            return []

        # 1. Preprocess raw data
        windows = self.prepare_windows(windows)

        # 2. Sort by score
        windows = self.rank_windows(windows)

        # 3. Try single DER
        single = self.pick_single(windows, required_kw)
        if single:
            return single

        # 4. Otherwise knapsack
        subset = self.knapsack_minimal_feasible(windows, required_kw)

        print("\n[OptimisationAgent] Selected DER set (true knapsack):")
        print(f"  Total: {sum(w['capacity_kw'] for w in subset)} kW (needed {required_kw} kW)")
        for w in subset:
            print(f"   - {w['id']} | {w['capacity_kw']} kW | RE {w['renewable_mix']}%")

        return subset

    def prepare_windows(self, windows):
        """Convert MW → kW and fill missing values."""
        for w in windows:
            w["capacity_kw"] = int((w.get("capacity_mw") or 0) * 1000)
        return windows

    def score(self, w):
        ren = w.get("renewable_mix") or 0
        ci  = w.get("carbon_intensity") or 999
        return ren * 2 - ci

    def rank_windows(self, windows):
        """Sort windows by score, print the best one."""
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

        if not best_subset:
            print("[OptimisationAgent] No feasible combination — selecting all DERs.")
            return windows

        return list(best_subset)
