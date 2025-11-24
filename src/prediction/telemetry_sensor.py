import random
from datetime import datetime, timezone

def now():
    return datetime.now(timezone.utc).isoformat()

class TelemetrySensor:
    """Simulates feeder telemetry from a grid operator."""

    def __init__(self, feeder_limit_kw=15000, overload_probability=0.30):
        self.feeder_limit_kw = feeder_limit_kw
        self.overload_probability = overload_probability

    def read(self):
        """Return a telemetry record."""

        overload = random.random() < self.overload_probability

        if overload:
            load = self.feeder_limit_kw + random.randint(2000, 15000)
        else:
            load = random.randint(9000, self.feeder_limit_kw - 200)

        return {
            "timestamp": now(),
            "current_load_kw": load,
            "voltage_kv": round(random.uniform(10.5, 11.0), 3),
            "frequency_hz": round(random.uniform(49.7, 50.1), 3),
        }
