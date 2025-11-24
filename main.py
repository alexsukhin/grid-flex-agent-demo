from src.prediction_agent import PredictionAgent
from src.optimisation_agent import OptimisationAgent
from src.dispatch_agent import DispatchAgent

from src.prediction_agent import PredictionAgent
from src.optimisation_agent import OptimisationAgent
from src.dispatch_agent import DispatchAgent
import time

def main():
    print("\n=== PROJECT REFLEX — FULL WORKFLOW ===")

    predictor  = PredictionAgent()
    optimiser  = OptimisationAgent()
    dispatcher = DispatchAgent()

    required_kw = 0

    while required_kw <= 0:
        required_kw = predictor.predict_overload()

        if required_kw <= 0:
            print("[System] Waiting for next telemetry sample...\n")
            time.sleep(1)   # check again in 2 seconds

    print(f"\n[System] Overload confirmed → Need {required_kw} kW")
    print("[System] Starting orchestration workflow...\n")

    # === Beckn workflow ===
    on_discover = dispatcher.discover()
    windows = dispatcher.extract_windows(on_discover)
    selected = optimiser.select_der(windows, required_kw)
    order_id = dispatcher.confirm(selected, required_kw)
    dispatcher.status(order_id)

    print("\n=== WORKFLOW COMPLETE ===")




if __name__ == "__main__":
    main()
