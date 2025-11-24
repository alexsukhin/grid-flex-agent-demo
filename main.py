from src.prediction.prediction_agent import PredictionAgent
from src.optimisation.optimisation_agent import OptimisationAgent
from src.dispatch.dispatch_agent import DispatchAgent
from src.audit_trail import AuditTrail
from src.llm.llm_agent import LLMAgent
from src.llm.prompts import explain_overload, explain_selection, explain_escalation
import time

SANDBOX = "https://deg-hackathon-bap-sandbox.becknprotocol.io/api"

def main():
    print("\n=== PROJECT REFLEX — FULL WORKFLOW ===")

    audit = AuditTrail()

    predictor  = PredictionAgent(audit)
    optimiser  = OptimisationAgent(audit)
    dispatcher = DispatchAgent(audit, SANDBOX)

    llm = LLMAgent(
        api_key="sk-DdBu2719G7iaw-ONtqazxNGmdE-ZhrNWPGVo68Y0mow"
    )

    required_kw = 0

    while required_kw <= 0:
        required_kw = predictor.predict_overload()
        if required_kw <= 0:
            print("[System] Waiting for next telemetry sample...\n")
            time.sleep(1)

    summary = llm.ask(explain_overload(audit.logs[-1]))
    audit.log_llm_output("overload_explanation", summary)
    print("\n[LLM] Overload explanation:\n", summary)


    print(f"\n[System] Overload confirmed - Need {required_kw} kW")

    on_discover = dispatcher.discover()
    windows = dispatcher.extract_windows(on_discover)
    selected = optimiser.select_der(windows, required_kw)

    summary = llm.ask(explain_selection(selected, required_kw))
    audit.log_llm_output("selection_explained", summary)
    print("\n[LLM] Selection explanation:\n", summary)

    order_id = dispatcher.confirm(selected, required_kw)
    dispatcher.status(order_id)

    print("\n=== WORKFLOW COMPLETE ===")

    audit.dump_json()

if __name__ == "__main__":
    main()
