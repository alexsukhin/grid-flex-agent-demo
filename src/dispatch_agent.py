import requests
import uuid
from datetime import datetime, timezone
import random

SANDBOX = "https://deg-hackathon-bap-sandbox.becknprotocol.io/api"


def now():
    return datetime.now(timezone.utc).isoformat()

class DispatchAgent:
    def __init__(self, audit):
        self.audit = audit
        self.transaction_id = str(uuid.uuid4())
        self.obp_id = f"obp-{uuid.uuid4()}"
        print(f"[DispatchAgent] Transaction: {self.transaction_id}")
        print(f"[DispatchAgent] OBP ID: {self.obp_id}")

    def discover(self):
        message_id = str(uuid.uuid4())

        self.audit.log_discover_sent({
            "message_id": message_id,
            "transaction_id": self.transaction_id,
            "obp_id": self.obp_id
        })

        payload = {
            "context": {
                "version": "2.0.0",
                "action": "discover",
                "domain": "beckn.one:DEG:compute-energy:1.0",
                "timestamp": now(),
                "message_id": message_id,
                "transaction_id": self.transaction_id,
                "bap_id": "ev-charging.sandbox1.com",
                "bap_uri": "https://ev-charging.sandbox1.com.com/bap",
                "ttl": "PT30S",
                "schema_context": [
                    "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/ComputeEnergy/v1/context.jsonld"
                ]
            },
            "message": {
                "text_search": "Grid flexibility windows",
                "filters": {
                    "type": "jsonpath",
                    "expression": "$[?(@.beckn:itemAttributes.beckn:gridParameters.renewableMix >= 70)]"
                }
            }
        }

        print("\n=== /discover ===")
        response = requests.post(f"{SANDBOX}/discover", json=payload)
        print("STATUS:", response.status_code)

        return response.json()

    def extract_windows(self, discover_json):
        windows = []

        catalogs = discover_json.get("message", {}).get("catalogs", [])
        for cat in catalogs:
            catalog_id = cat.get("beckn:id")

            offer_lookup = {}
            for offer in cat.get("beckn:offers", []):
                price_obj = offer.get("beckn:price", {})

                for item_id in offer.get("beckn:items", []):
                    offer_lookup[item_id] = {
                        "price_kw": price_obj.get("value"),
                        "currency": price_obj.get("currency"),
                        "price_stability": offer.get("beckn:offerAttributes", {})
                                                .get("beckn:priceStability")
                    }

            for item in cat.get("beckn:items", []):

                item_id = item.get("beckn:id")
                offer = offer_lookup.get(item_id, {})

                attrs = item.get("beckn:itemAttributes", {})
                g = attrs.get("beckn:gridParameters", {})
                c = attrs.get("beckn:capacityParameters", {})
                t = attrs.get("beckn:timeWindow", {})

                loc = item.get("beckn:availableAt", [{}])[0]
                address = loc.get("address", {})

                provider = item.get("beckn:provider", {})

                # Synthetic fields for realism
                comfort_penalty = random.uniform(0.0, 1.0)
                availability_score = random.uniform(0.7, 1.0)
                response_time_s = random.randint(1, 10)

                windows.append({
                    "id": item_id,
                    "catalog_id": catalog_id,

                    "provider_id": provider.get("beckn:id"),
                    "provider_name": provider.get("beckn:descriptor", {})
                                            .get("schema:name"),

                    "renewable_mix": g.get("renewableMix"),
                    "carbon_intensity": g.get("carbonIntensity"),
                    "capacity_mw": c.get("availableCapacity"),

                    "price_kw": offer.get("price_kw"),
                    "price_currency": offer.get("currency"),
                    "price_stability": offer.get("price_stability"),

                    "window_start": t.get("start"),
                    "window_end": t.get("end"),
                    "window_duration": t.get("duration"),
                    
                    "reservation_required": c.get("reservationRequired"),

                    "comfort_penalty": comfort_penalty,
                    "availability_score": availability_score,
                    "response_time_s": response_time_s,

                    "region": g.get("gridArea"),
                    "grid_zone": g.get("gridZone"),
                    "address_full": address.get("streetAddress"),
                })

        print(f"[DispatchAgent] Extracted {len(windows)} DER windows")

        self.audit.log_discover_received({
            "count": len(windows),
            "obp_id": self.obp_id
        })
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
        order_items = []

        for idx, w in enumerate(selected_windows):

            requested_reduction_kw = min(required_kw, (w["capacity_mw"] or 0) * 1000)

            der_meta = {
                "@type": "beckn:DERMetadata",
                "gridRegion": w.get("region"),
                "gridZone": w.get("grid_zone"),
                "renewableMix": w.get("renewable_mix"),
                "carbonIntensity": w.get("carbon_intensity"),
                "capacityMW": w.get("capacity_mw"),
                "pricePerKW": w.get("price_kw"),
                "priceCurrency": w.get("price_currency"),
                "priceStability": w.get("price_stability"),
                "comfortPenalty": w.get("comfort_penalty"),
                "availabilityScore": w.get("availability_score"),
                "responseTimeSeconds": w.get("response_time_s"),
                "reservationRequired": w.get("reservation_required"),
                "windowStart": w.get("window_start"),
                "windowEnd": w.get("window_end"),
                "windowDuration": w.get("window_duration"),
                "location": w.get("address_full")
            }

            order_items.append({
                "@type": "beckn:OrderItem",
                "beckn:lineId": f"der-{idx+1}",
                "beckn:orderedItem": w["id"],

                "beckn:orderItemAttributes": {
                    "@type": "beckn:DemandFlexibilityActivation",

                    "beckn:consumerId": w["provider_id"],

                    "beckn:requestedReduction": requested_reduction_kw,
                    "beckn:requestedReductionUnit": "kW",

                    "beckn:activationTime": now(),
                    "beckn:duration": w["window_duration"],

                    "beckn:derMetadata": der_meta
                }
            })

        payload = {
            "context": {
                "version": "2.0.0",
                "action": "confirm",
                "domain": "beckn.one:DEG:demand-flexibility:1.0",
                "timestamp": now(),
                "message_id": str(uuid.uuid4()),
                "transaction_id": self.transaction_id,
                "bap_id": "ev-charging.sandbox1.com",
                "bap_uri": "https://ev-charging.sandbox1.com/bap",
                "bpp_id": "ev-charging.sandbox1.com",
                "bpp_uri": "https://ev-charging.sandbox1.com/bpp",
                "ttl": "PT30S"
            },

            "message": {
                "order": {
                    "@type": "beckn:Order",
                    "order_id": order_id,

                    "orderItems": order_items,

                    "beckn:totalRequestedReduction": required_kw,
                    "beckn:totalRequestedReductionUnit": "kW",

                    "beckn:fulfillment": {
                        "@type": "beckn:Fulfillment",
                        "beckn:mode": "DEMAND_RESPONSE",
                        "beckn:status": "PENDING"
                    }
                }
            }
        }

        print("\n=== /confirm ===")
        response = requests.post(f"{SANDBOX}/confirm", json=payload)
        print("STATUS:", response.status_code)
        return order_id



    def status(self, order_id):
        self.audit.log_status_requested({
            "order_id": order_id,
            "transaction_id": self.transaction_id,
            "obp_id": self.obp_id
        })

        payload = {
            "context": {
                "version": "2.0.0",
                "action": "status",
                "domain": "beckn.one:DEG:demand-flexibility:1.0",
                "timestamp": now(),
                "message_id": str(uuid.uuid4()),
                "transaction_id": self.transaction_id,
                "bap_id": "ev-charging.sandbox1.com",
                "bap_uri": "https://ev-charging.sandbox1.com/bap",
                "bpp_id": "ev-charging.sandbox1.com",
                "bpp_uri": "https://ev-charging.sandbox1.com/bpp",
                "ttl": "PT30S"
            },
            "message": {
                "order_id": order_id
            }
        }

        print("\n=== /status ===")
        response = requests.post(f"{SANDBOX}/status", json=payload)
        print("STATUS:", response.status_code)
        return response.text
