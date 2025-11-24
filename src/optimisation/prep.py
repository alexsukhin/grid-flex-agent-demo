class WindowPreprocessor:
    """Adds derived fields (e.g., kW) and normalizes window data."""

    def prepare(self, windows):
        for w in windows:
            w["capacity_kw"] = int((w.get("capacity_mw") or 0) * 1000)
        return windows
