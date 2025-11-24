from src.prediction_agent import PredictionAgent
from src.optimisation_agent import OptimisationAgent
from src.dispatch_agent import DispatchAgent


def main():
    print("\n=== PROJECT REFLEX — FULL WORKFLOW ===")

    predictor  = PredictionAgent()
    optimiser  = OptimisationAgent()
    dispatcher = DispatchAgent()

    required_kw = predictor.predict_overload()

    on_discover = dispatcher.discover()

    windows = dispatcher.extract_windows(on_discover)

    selected = optimiser.select_der(windows, required_kw)

    order_id = dispatcher.confirm(selected, required_kw)

    dispatcher.status(order_id)

    print("\n=== WORKFLOW COMPLETE ===")



if __name__ == "__main__":
    main()
