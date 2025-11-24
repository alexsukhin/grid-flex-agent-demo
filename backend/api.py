from fastapi import APIRouter
from fastapi.responses import JSONResponse
import time

from src.prediction.prediction_agent import PredictionAgent
from src.optimisation.optimisation_agent import OptimisationAgent
from src.dispatch.dispatch_agent import DispatchAgent
from src.audit_trail import AuditTrail
from src.llm.llm_agent import LLMAgent
from src.llm.prompts import (
    explain_overload,
    explain_selection,
    explain_confirm,
    explain_status,
)

SANDBOX = "https://deg-hackathon-bap-sandbox.becknprotocol.io/api"

router = APIRouter()


@router.get("/workflow/run")
def run_workflow():
    """
    Run the full Project Reflex workflow and return a JSON summary.
    """

    try:
        audit = AuditTrail()
        predictor = PredictionAgent(audit)
        optimiser = OptimisationAgent(audit)
        dispatcher = DispatchAgent(audit, SANDBOX)
        llm = LLMAgent()

        required_kw = 0
        while required_kw <= 0:
            required_kw = predictor.predict_overload()
            if required_kw <= 0:
                pass

        overload_future = llm.ask_async(explain_overload(audit.logs[-1]))

        start = time.time()

        on_discover = dispatcher.discover()
        windows = dispatcher.extract_windows(on_discover)

        selected, mode, meta = optimiser.select_der(windows, required_kw)

        selection_future = llm.ask_async(
            explain_selection(selected, required_kw, mode, meta)
        )

        confirm_resp = dispatcher.confirm(selected, required_kw, mode)
        order_id = confirm_resp["order_id"]
        on_confirm = confirm_resp["on_confirm"]

        confirm_future = llm.ask_async(explain_confirm(on_confirm))

        on_status = dispatcher.status(order_id)
        status_future = llm.ask_async(explain_status(on_status))

        end = time.time()

        overload_msg = overload_future.result()
        selection_msg = selection_future.result()
        confirm_msg = confirm_future.result()
        status_msg = status_future.result()

        return JSONResponse(
            {
                "required_kw": required_kw,
                "mode": mode,
                "meta": meta,
                "selected": selected,
                "order_id": order_id,
                "discover_raw": on_discover,
                "confirm_raw": on_confirm,
                "status_raw": on_status,
                "llm": {
                    "overload": overload_msg,
                    "selection": selection_msg,
                    "confirm": confirm_msg,
                    "status": status_msg,
                },
                "performance_seconds": round(end - start, 3),
                "audit_log": audit.logs,
            }
        )

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
