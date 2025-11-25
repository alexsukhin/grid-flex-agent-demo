from datetime import datetime, timezone, timedelta
import uuid

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
    
    def build_confirm(self, order_id, windows, required_kw, mode):

        event_id = f"df-event-{uuid.uuid4()}"
        event_start = now()
        event_end = (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()

        if mode == "incentive":
            estimated_incentive = round(required_kw * 0.10, 2)
            order_type = "resource_activation"
            priority = "normal"
            severity = "medium"
        else:
            estimated_incentive = 0.0
            order_type = "emergency_curtailment"
            priority = "highest"
            severity = "high"

        def build_event_details():
            return {
                "@context": "https://raw.githubusercontent.com/beckn/protocol-specifications-new/refs/heads/draft/schema/DemandFlexibility/v1/context.jsonld",
                "@type": "beckn:DemandFlexibilityEventDetails",
                "beckn:eventId": event_id,
                "beckn:eventType": "peak_demand_surge",
                "beckn:eventSeverity": severity,
                "beckn:gridFrequency": 49.85,
                "beckn:gridFrequencyUnit": "Hz"
            }

        def der_meta(w):
            return {
                "@type": "beckn:DERMetadata",
                "gridRegion": w.get("region"),
                "gridZone": w.get("grid_zone"),
                "renewableMix": w.get("renewable_mix"),
                "carbonIntensity": w.get("carbon_intensity"),
                "capacityMW": w.get("capacity_mw"),
                "reservationRequired": w.get("reservation_required"),
                "responseTimeSeconds": w.get("response_time_s"),
                "comfortPenalty": w.get("comfort_penalty"),
                "availabilityScore": w.get("availability_score"),
                "windowStart": w.get("window_start"),
                "windowEnd": w.get("window_end"),
                "windowDuration": w.get("window_duration"),
                "location": w.get("address_full"),
                "pricePerKW": None if mode == "emergency" else w.get("price_kw"),
                "priceCurrency": None if mode == "emergency" else w.get("price_currency"),
            }

        order_items = []
        for idx, w in enumerate(windows):
            req_kw = min(required_kw, int(w.get("capacity_mw", 0) * 1000))

            order_items.append({
                "@type": "beckn:OrderItem",
                "beckn:lineId": f"activation-{idx+1}",
                "beckn:orderedItem": w["id"],
                "beckn:orderItemAttributes": {
                    "@type": "beckn:DemandFlexibilityActivation",
                    "beckn:consumerId": w["provider_id"],
                    "beckn:requestedReduction": req_kw,
                    "beckn:requestedReductionUnit": "kW",
                    "beckn:activationTime": event_start,
                    "beckn:duration": w.get("window_duration"),
                    "beckn:eventDetails": build_event_details(),
                    "beckn:derMetadata": der_meta(w),
                }
            })

        payment_block = None
        if mode == "incentive":
            payment_block = {
                "@type": "beckn:Payment",
                "beckn:status": "PENDING",
                "beckn:paymentAttributes": {
                    "@type": "beckn:DemandFlexibilityIncentive",
                    "beckn:totalEstimatedIncentive": estimated_incentive,
                    "beckn:currency": "GBP",
                    "beckn:paymentMethod": "monthly_billing_adjustment",
                    "beckn:settlementFrequency": "monthly",
                }
            }

        order = {
            "@type": "beckn:Order",
            "beckn:id": order_id,
            "beckn:orderStatus": "PENDING",
            "beckn:seller": "ev-charging.sandbox1.com",
            "beckn:buyer": "ev-charging.sandbox1.com",
            "beckn:orderItems": order_items,
            "beckn:fulfillment": {
                "@type": "beckn:Fulfillment",
                "beckn:id": f"fulfillment-{order_id}",
                "beckn:mode": "DEMAND_RESPONSE",
                "beckn:status": "PENDING",
                "beckn:deliveryAttributes": {
                    "@type": "beckn:DemandFlexibilityEvent",
                    "beckn:eventId": event_id,
                    "beckn:eventType": "peak_demand_surge",
                    "beckn:eventSeverity": severity,
                    "beckn:eventStartTime": event_start,
                    "beckn:eventEndTime": event_end,
                    "beckn:totalRequestedReduction": required_kw,
                    "beckn:totalRequestedReductionUnit": "kW"
                }
            },
            "beckn:orderAttributes": {
                "@type": "beckn:DemandFlexibilityOrder",
                "beckn:orderType": order_type,
                "beckn:priority": priority,
                "beckn:confirmationTimestamp": now()
            }
        }

        if payment_block:
            order["beckn:payment"] = payment_block

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
                "order": order
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
