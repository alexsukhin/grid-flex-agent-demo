class OptimisationAgent:
    def select_der(self, windows, required_kw):
        if not windows:
            print("[OptimisationAgent] No DER windows to evaluate!")
            return None

        required_mw = required_kw / 1000

        def safe(x):
            return 0 if x is None else x

        eligible = [
            w for w in windows
            if safe(w.get("capacity_mw")) >= required_mw
        ]

        if not eligible:
            print(f"[OptimisationAgent] No DER windows can supply {required_mw} MW.")
            print("[OptimisationAgent] Falling back to 'best available' window.")
            eligible = windows

        def score(w):
            return (
                safe(w.get("renewable_mix")) * 2 +
                safe(w.get("capacity_mw")) * 10 -
                safe(w.get("carbon_intensity"))
            )

        best = max(eligible, key=score)

        print("\n[OptimisationAgent] Selected DER Window:")
        for k, v in best.items():
            print(f"  {k}: {v}")

        return best
