import random

class WindowExtractor:
    """Converts Beckn discovery into a list of normalised DER window dicts."""

    def extract(self, doc):
        windows = []

        catalogs = doc.get("message", {}).get("catalogs", [])
        for cat in catalogs:
            catalog_id = cat.get("beckn:id")

            # Build offer to item map
            offer_lookup = {}
            for offer in cat.get("beckn:offers", []):
                for item_id in offer.get("beckn:items", []):
                    price = offer.get("beckn:price", {})
                    offer_lookup[item_id] = {
                        "price_kw": price.get("value"),
                        "currency": price.get("currency"),
                        "price_stability": offer.get("beckn:offerAttributes", {})
                                              .get("beckn:priceStability")
                    }

            # Convert items into windows
            for item in cat.get("beckn:items", []):
                item_id = item.get("beckn:id")
                offer = offer_lookup.get(item_id, {})
                attrs = item.get("beckn:itemAttributes", {})

                g = attrs.get("beckn:gridParameters", {})
                c = attrs.get("beckn:capacityParameters", {})
                t = attrs.get("beckn:timeWindow", {})
                provider = item.get("beckn:provider", {})
                address = item.get("beckn:availableAt", [{}])[0].get("address", {})

                windows.append({
                    "id": item_id,
                    "catalog_id": catalog_id,
                    "provider_id": provider.get("beckn:id"),
                    "provider_name": provider.get("beckn:descriptor", {}).get("schema:name"),

                    "renewable_mix": g.get("renewableMix"),
                    "carbon_intensity": g.get("carbonIntensity"),
                    "capacity_mw": c.get("availableCapacity"),
                    "reservation_required": c.get("reservationRequired"),

                    "price_kw": offer.get("price_kw"),
                    "price_currency": offer.get("currency"),
                    "price_stability": offer.get("price_stability"),

                    "window_start": t.get("start"),
                    "window_end": t.get("end"),
                    "window_duration": t.get("duration"),

                    "comfort_penalty": random.uniform(0.0, 1.0),
                    "availability_score": random.uniform(0.7, 1.0),
                    "response_time_s": random.randint(1, 10),

                    "region": g.get("gridArea"),
                    "grid_zone": g.get("gridZone"),
                    "address_full": address.get("streetAddress"),
                })

        return windows
