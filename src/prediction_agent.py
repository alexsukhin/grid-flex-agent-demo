import random

class PredictionAgent:
    def predict_overload(self):
        overload_kw = random.choice([500, 800, 1000, 1500])
        print(f"[PredictionAgent] Overload detected — Need {overload_kw} kW flexibility")
        return overload_kw
