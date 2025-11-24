import itertools

class KnapsackSolver:
    """Finds minimal-overshoot subset to meet flexibility requirement."""

    def solve(self, windows, required_kw):
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

        return list(best_subset)
