from .telemetry_sensor import TelemetrySensor
from .exponential_smoother import ExponentialSmoother

class PredictionAgent:
    """Coordinator for telemetry → forecasting → overload logic."""

    def __init__(self, audit, feeder_limit_kw=15000):
        self.audit = audit
        self.sensor = TelemetrySensor()
        self.forecaster = ExponentialSmoother(alpha=0.4)
        self.feeder_limit_kw = feeder_limit_kw

    def predict_overload(self):
        """Retrieve telemetry, run forecast, and determine overload."""

        telemetry = self.sensor.read()
        forecast_kw = self.forecaster.predict(telemetry["current_load_kw"])

        self.audit.log_prediction({
            **telemetry,
            "forecast_kw": forecast_kw
        })

        self.print_telemetry(telemetry, forecast_kw)

        if forecast_kw > self.feeder_limit_kw:
            deficit = int(forecast_kw - self.feeder_limit_kw)
            self.audit.log_overload(deficit)
            print(f"[PredictionAgent] Forecast overload — Need {deficit} kW")
            return deficit

        print("[PredictionAgent] No overload detected.")
        return 0

    def print_telemetry(self, t, forecast_kw):
        print(f"\n[PredictionAgent] Feeder telemetry @ {t['timestamp']}")
        print(f"  Load:      {t['current_load_kw']} kW")
        print(f"  Forecast:  {int(forecast_kw)} kW (exp smoothing)")
        print(f"  Voltage:   {t['voltage_kv']} kV")
        print(f"  Frequency: {t['frequency_hz']} Hz")
