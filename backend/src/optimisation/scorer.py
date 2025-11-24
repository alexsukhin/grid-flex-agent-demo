class DERScorer:
    """Computes composite scores for flexibility windows."""

    def score(self, w):
        ren = w.get("renewable_mix") or 0
        ci  = w.get("carbon_intensity") or 999
        cost = w.get("price_kw") or 0.15
        comfort = w.get("comfort_penalty") or 0.5
        avail = w.get("availability_score") or 0.8
        response = w.get("response_time_s") or 5

        return (
            ren * 1.5
            - ci * 0.5
            - cost * 40
            - comfort * 20
            + avail * 30
            - response * 2
        )

    def rank(self, windows):
        ranked = sorted(windows, key=self.score, reverse=True)

        for w in ranked:
            w["composite_score"] = self.score(w)

        return ranked
