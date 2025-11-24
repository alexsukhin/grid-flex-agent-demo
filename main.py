from src.prediction.prediction_agent import PredictionAgent
from src.optimisation.optimisation_agent import OptimisationAgent
from src.dispatch.dispatch_agent import DispatchAgent
from src.audit_trail import AuditTrail
import time

SANDBOX = "https://deg-hackathon-bap-sandbox.becknprotocol.io/api"

def main():
    print("\n=== PROJECT REFLEX — FULL WORKFLOW ===")

    audit = AuditTrail()

    predictor  = PredictionAgent(audit)
    optimiser  = OptimisationAgent(audit)
    dispatcher = DispatchAgent(audit, SANDBOX)

    required_kw = 0

    while required_kw <= 0:
        required_kw = predictor.predict_overload()
        if required_kw <= 0:
            print("[System] Waiting for next telemetry sample...\n")
            time.sleep(1)

    print(f"\n[System] Overload confirmed - Need {required_kw} kW")

    on_discover = dispatcher.discover()
    windows = dispatcher.extract_windows(on_discover)
    selected = optimiser.select_der(windows, required_kw)
    order_id = dispatcher.confirm(selected, required_kw)
    dispatcher.status(order_id)

    print("\n=== WORKFLOW COMPLETE ===")

    audit.dump_json()




if __name__ == "__main__":
    main()
