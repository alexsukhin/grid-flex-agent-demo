class ExponentialSmoother:
    """Simple exponential smoothing model for load forecasting."""

    def __init__(self, alpha=0.4):
        self.alpha = alpha
        self.last = None

    def predict(self, actual):
        """Update forecast based on new observation."""
        if self.last is None:
            self.last = actual
        else:
            self.last = self.alpha * actual + (1 - self.alpha) * self.last

        return self.last
