def explain_overload(data):
    return f"""
    You are an AI grid co-pilot. Explain this overload event in one 
    simple sentence. Keep it friendly and non-technical.

    Telemetry:
    {data}
    """

def explain_selection(selected, required_kw, mode, meta):
    return f"""
    You are an AI assistant explaining why these DER windows were selected.

    Required: {required_kw} kW  
    Mode: {mode.upper()}
    IMPORTANT:
    - If mode = EMERGENCY → Incentives do NOT apply. Do NOT mention money. Do NOT mention settlement or billings.
    - If mode = INCENTIVE → You may mention incentives briefly.

    Meta:
    {meta}

    Selected windows:
    {selected}

    Explain the reasoning in 1–2 concise sentences.
    """

def explain_escalation(reason):
    return f"""
    Explain this escalation in one simple sentence.

    IMPORTANT:
    - If mode = EMERGENCY → Incentives do NOT apply. Do NOT mention money.
    - If mode = INCENTIVE → You may mention incentives briefly.

    Reason: {reason}
    """

def explain_confirm(confirm_json):
    return f"""
    Summarise this confirmation event in 2–3 sentences for a grid operator:

    IMPORTANT:
    - If mode = EMERGENCY → Incentives do NOT apply. Do NOT mention money.
    - If mode = INCENTIVE → You may mention incentives briefly.

    {confirm_json}
    """

def explain_status(status_json):
    return f"""
    Explain what happened in this flexibility event. 
    Keep it to 2–4 sentences, simple and clear.

    IMPORTANT:
    - If mode = EMERGENCY → Incentives do NOT apply. Do NOT mention money.
    - If mode = INCENTIVE → You may mention incentives briefly.

    {status_json}
    """