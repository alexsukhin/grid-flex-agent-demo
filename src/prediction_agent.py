import random
from datetime import datetime, timezone

def now():
    return datetime.now(timezone.utc).isoformat()


class PredictionAgent:
    def __init__(self):
        self.feeder_limit_kw = 15_000

    def read_feeder_data(self):
        overload_roll = random.random() < 0.30

        if overload_roll:
            current_load = self.feeder_limit_kw + random.randint(2000, 15000)
        else:
            current_load = random.randint(9000, 14800)

        return {
            "timestamp": now(),
            "current_load_kw": current_load,
            "voltage_kv": round(random.uniform(10.5, 11.0), 3),
            "frequency_hz": round(random.uniform(49.7, 50.1), 3),
        }

    def predict_overload(self):
        data = self.read_feeder_data()

        print(f"\n[PredictionAgent] Feeder telemetry @ {data['timestamp']}")
        print(f"  Load: {data['current_load_kw']} kW")
        print(f"  Voltage: {data['voltage_kv']} kV")
        print(f"  Frequency: {data['frequency_hz']} Hz")

        if data["current_load_kw"] > self.feeder_limit_kw:
            deficit = data["current_load_kw"] - self.feeder_limit_kw
            print(f"[PredictionAgent] Overload detected — Need {deficit} kW flexibility")
            return deficit

        print("[PredictionAgent] No overload detected — no flexibility needed")
        return 0
