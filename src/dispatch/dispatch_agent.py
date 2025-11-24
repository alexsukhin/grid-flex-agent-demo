import uuid
from datetime import datetime, timezone
from .payload_builder import PayloadBuilder
from .window_extractor import WindowExtractor
from .api_client import BecknAPIClient


def now():
    return datetime.now(timezone.utc).isoformat()


class DispatchAgent:
    """Coordinates Beckn discovery -> selection -> confirm -> status"""

    def __init__(self, audit, sandbox_url):
        self.audit = audit
        self.transaction_id = str(uuid.uuid4())
        self.obp_id = f"obp-{uuid.uuid4()}"

        print(f"[DispatchAgent] Transaction: {self.transaction_id}")
        print(f"[DispatchAgent] OBP ID: {self.obp_id}")

        self.client = BecknAPIClient(sandbox_url)
        self.payloads = PayloadBuilder(self.transaction_id)
        self.extractor = WindowExtractor()

    def discover(self):
        message_id = str(uuid.uuid4())

        self.audit.log_discover_sent({
            "message_id": message_id,
            "obp_id": self.obp_id,
            "transaction_id": self.transaction_id
        })

        payload = self.payloads.build_discover(message_id)

        print("\n=== /discover ===")
        return self.client.post("/discover", payload)

    def extract_windows(self, discover_json):
        windows = self.extractor.extract(discover_json)

        self.audit.log_discover_received({
            "count": len(windows),
            "obp_id": self.obp_id
        })

        print(f"[DispatchAgent] Extracted {len(windows)} DER windows")
        return windows

    def confirm(self, selected_windows, required_kw):
        if not isinstance(selected_windows, list):
            selected_windows = [selected_windows]

        order_id = f"order-{uuid.uuid4()}"

        self.audit.log_confirm_sent({
            "order_id": order_id,
            "selected_ids": [w["id"] for w in selected_windows],
            "transaction_id": self.transaction_id,
            "obp_id": self.obp_id
        })

        payload = self.payloads.build_confirm(order_id, selected_windows, required_kw)

        print("\n=== /confirm ===")
        self.client.post("/confirm", payload)

        return order_id

    def status(self, order_id):
        self.audit.log_status_requested({
            "order_id": order_id,
            "transaction_id": self.transaction_id,
            "obp_id": self.obp_id
        })

        payload = self.payloads.build_status(order_id)

        print("\n=== /status ===")
        return self.client.post("/status", payload)
