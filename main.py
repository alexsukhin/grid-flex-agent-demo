from src.prediction.prediction_agent import PredictionAgent
from src.optimisation.optimisation_agent import OptimisationAgent
from src.dispatch.dispatch_agent import DispatchAgent
from src.audit_trail import AuditTrail
from src.llm.llm_agent import LLMAgent
from src.llm.prompts import explain_overload, explain_selection, explain_confirm, explain_status
import time

SANDBOX = "https://deg-hackathon-bap-sandbox.becknprotocol.io/api"

def main():
    print("\n=== PROJECT REFLEX — FULL WORKFLOW ===")

    audit = AuditTrail()

    predictor  = PredictionAgent(audit)
    optimiser  = OptimisationAgent(audit)
    dispatcher = DispatchAgent(audit, SANDBOX)

    llm = LLMAgent()

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

    selected, mode, meta = optimiser.select_der(windows, required_kw)

    summary = llm.ask(explain_selection(selected, required_kw, mode, meta))
    audit.log_llm_output("selection_explained", summary)
    print("\n[LLM] Selection explanation:\n", summary)

    confirm_resp = dispatcher.confirm(selected, required_kw, mode)
    
    order_id = confirm_resp["order_id"]
    on_confirm = confirm_resp["on_confirm"]

    print("[LLM] Confirm explanation:")
    print(llm.ask(explain_confirm(on_confirm)))

    dispatcher.status(order_id)
    on_status = dispatcher.status(order_id)  
    print("[LLM] Status explanation:")
    print(llm.ask(explain_status(on_status)))

    print("\n=== WORKFLOW COMPLETE ===")

    audit.dump_json()

if __name__ == "__main__":
    main()
