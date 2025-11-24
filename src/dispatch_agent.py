import requests
import uuid
from datetime import datetime, timezone

SANDBOX = "https://deg-hackathon-bap-sandbox.becknprotocol.io/api"


def now():
    return datetime.now(timezone.utc).isoformat()


class DispatchAgent:
    def __init__(self):
        self.transaction_id = str(uuid.uuid4())
        print(f"[DispatchAgent] Transaction: {self.transaction_id}")

    def discover(self):
        message_id = str(uuid.uuid4())

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
        r = requests.post(f"{SANDBOX}/discover", json=payload)
        print("STATUS:", r.status_code)

        print(r.json())

        return r.json()

    def extract_windows(self, discover_json):
        windows = []

        catalogs = discover_json.get("message", {}).get("catalogs", [])

        for cat in catalogs:
            catalog_id = cat.get("beckn:id")
            catalog_validity = cat.get("beckn:validity", {})

            for item in cat.get("beckn:items", []):
                attrs = item.get("beckn:itemAttributes", {})
                g = attrs.get("beckn:gridParameters", {})
                c = attrs.get("beckn:capacityParameters", {})
                t = attrs.get("beckn:timeWindow", {})

                loc = item.get("beckn:availableAt", [{}])[0]
                geo = loc.get("geo", {})
                address = loc.get("address", {})

                provider = item.get("beckn:provider", {})
                descriptor = item.get("beckn:descriptor", {})

                windows.append({
                    "id": item.get("beckn:id"),
                    "catalog_id": catalog_id,

                    "provider_id": provider.get("beckn:id"),
                    "provider_name": provider.get("beckn:descriptor", {}).get("schema:name"),

                    "item_name": descriptor.get("schema:name"),
                    "item_description": descriptor.get("beckn:shortDesc"),

                    "region": g.get("gridArea"),
                    "grid_zone": g.get("gridZone"),
                    "renewable_mix": g.get("renewableMix"),
                    "renewable_mix_unit": g.get("renewableMixUnit"),
                    "carbon_intensity": g.get("carbonIntensity"),
                    "carbon_intensity_unit": g.get("carbonIntensityUnit"),

                    "capacity_mw": c.get("availableCapacity"),
                    "capacity_unit": c.get("capacityUnit"),
                    "reservation_required": c.get("reservationRequired"),

                    "window_start": t.get("start"),
                    "window_end": t.get("end"),
                    "window_duration": t.get("duration"),
                    "catalog_start": catalog_validity.get("schema:startDate"),
                    "catalog_end": catalog_validity.get("schema:endDate"),

                    "location_polygon": geo.get("coordinates"),
                    "address_locality": address.get("addressLocality"),
                    "address_region": address.get("addressRegion"),
                    "address_country": address.get("addressCountry"),
                    "address_full": address.get("streetAddress"),
                })

        print(f"[DispatchAgent] Extracted {len(windows)} DER windows")
        return windows

    def confirm(self, selected_window, required_kw):
        order_id = f"order-{uuid.uuid4()}"

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

                    "selected_window": {
                        "id": selected_window["id"],
                        "item_name": selected_window["item_name"],
                        "item_description": selected_window["item_description"],
                        "region": selected_window["region"],
                        "grid_zone": selected_window["grid_zone"],
                        "provider_name": selected_window["provider_name"],
                    },

                    "activation_parameters": {
                        "requested_reduction_kw": required_kw,
                        "renewable_mix": selected_window["renewable_mix"],
                        "renewable_mix_unit": selected_window["renewable_mix_unit"],
                        "carbon_intensity": selected_window["carbon_intensity"],
                        "carbon_intensity_unit": selected_window["carbon_intensity_unit"],
                        "capacity_mw": selected_window["capacity_mw"],
                        "capacity_unit": selected_window["capacity_unit"],
                        "reservation_required": selected_window["reservation_required"],
                    },

                    "time_window": {
                        "start": selected_window["window_start"],
                        "end": selected_window["window_end"],
                        "duration": selected_window["window_duration"]
                    },

                    "location": {
                        "polygon": selected_window["location_polygon"],
                        "locality": selected_window["address_locality"],
                        "region": selected_window["address_region"],
                        "country": selected_window["address_country"],
                        "full_address": selected_window["address_full"]
                    }
                }
            }
        }

        print("\n=== /confirm ===")
        r = requests.post(f"{SANDBOX}/confirm", json=payload)
        print("STATUS:", r.status_code)
        return order_id


    def status(self, order_id):
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
        r = requests.post(f"{SANDBOX}/status", json=payload)
        print("STATUS:", r.status_code)
        return r.text
