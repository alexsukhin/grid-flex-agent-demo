from fastapi import APIRouter
from fastapi.responses import JSONResponse
import time
import uuid

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

LLM_SESSIONS = {}
SESSION_TTL_SECONDS = 300 


@router.get("/workflow/run")
def run_workflow():
    """
    Run the full Project Reflex workflow and return a JSON summary
    *without* waiting for LLM responses.
    The LLM summaries are computed in the background and can be fetched
    via /workflow/llm/{session_id}.
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

        session_id = str(uuid.uuid4())
        LLM_SESSIONS[session_id] = {
            "created_at": time.time(),
            "overload": overload_future,
            "selection": selection_future,
            "confirm": confirm_future,
            "status": status_future,
        }

        return JSONResponse(
            {
                "session_id": session_id,
                "required_kw": required_kw,
                "mode": mode,
                "meta": meta,
                "selected": selected,
                "order_id": order_id,
                "all_windows": windows,
                "discover_raw": on_discover,
                "confirm_raw": on_confirm,
                "status_raw": on_status,
                "llm": None,
                "performance_seconds": round(end - start, 3),
                "audit_log": audit.logs,
            }
        )

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.get("/workflow/llm/{session_id}")
def get_llm_summaries(session_id: str):
    """
    Return LLM summaries for a given workflow session.
    If a summary isn't ready yet, it returns null for that field.
    """
    session = LLM_SESSIONS.get(session_id)
    if not session:
        return JSONResponse(
            {"error": "unknown_session", "session_id": session_id},
            status_code=404,
        )

    def safe_result(future):
        if not future.done():
            return None
        try:
            return future.result()
        except Exception as e:
            return f"LLM error: {e}"

    overload_msg = safe_result(session["overload"])
    selection_msg = safe_result(session["selection"])
    confirm_msg = safe_result(session["confirm"])
    status_msg = safe_result(session["status"])

    llm = {
        "overload": overload_msg,
        "selection": selection_msg,
        "confirm": confirm_msg,
        "status": status_msg,
    }

    complete = all(v is not None for v in llm.values())

    return JSONResponse(
        {
            **llm,
            "complete": complete,
        }
    )
