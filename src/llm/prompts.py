def explain_overload(data):
    return f"""
    You are an AI grid co-pilot. Explain this overload event in one 
    simple sentence. Keep it friendly and non-technical.

    Telemetry:
    {data}
    """

def explain_selection(windows, required_kw):
    return f"""
    You are an AI assistant summarising the optimisation decision.
    Explain in one to two short sentences why these DER windows were chosen.

    Required flexibility: {required_kw} kW
    Selected windows:
    {windows}
    """

def explain_escalation(reason):
    return f"""
    Explain this escalation in one simple sentence.

    Reason: {reason}
    """