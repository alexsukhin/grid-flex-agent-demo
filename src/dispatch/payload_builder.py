from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc).isoformat()


class PayloadBuilder:
    """Builds discover/confirm/status payloads using correct Beckn format."""

    def __init__(self, transaction_id):
        self.transaction_id = transaction_id

    def build_discover(self, message_id):
        return {
            "context": {
                "version": "2.0.0",
                "action": "discover",
                "domain": "beckn.one:DEG:compute-energy:1.0",
                "timestamp": now(),
                "message_id": message_id,
                "transaction_id": self.transaction_id,
                "bap_id": "ev-charging.sandbox1.com",
                "bap_uri": "https://ev-charging.sandbox1.com/bap",
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

    def build_confirm(self, order_id, windows, required_kw):

        def der_meta(w):
            return {
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

        order_items = []
        for idx, w in enumerate(windows):
            req_kw = min(required_kw, (w.get("capacity_mw") or 0) * 1000)

            order_items.append({
                "@type": "beckn:OrderItem",
                "beckn:lineId": f"der-{idx+1}",
                "beckn:orderedItem": w["id"],
                "beckn:orderItemAttributes": {
                    "@type": "beckn:DemandFlexibilityActivation",
                    "beckn:consumerId": w["provider_id"],
                    "beckn:requestedReduction": req_kw,
                    "beckn:requestedReductionUnit": "kW",
                    "beckn:activationTime": now(),
                    "beckn:duration": w["window_duration"],
                    "beckn:derMetadata": der_meta(w)
                }
            })

        return {
            "context": {
                "version": "2.0.0",
                "action": "confirm",
                "domain": "beckn.one:DEG:demand-flexibility:1.0",
                "timestamp": now(),
                "message_id": order_id,
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

    def build_status(self, order_id):
        return {
            "context": {
                "version": "2.0.0",
                "action": "status",
                "domain": "beckn.one:DEG:demand-flexibility:1.0",
                "timestamp": now(),
                "message_id": order_id,
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
