"""
fetch_data.py

Scrapes self-storage facilities in San Francisco using Geoapify Places API
(free tier: 3,000 requests/day, no billing card required).
Saves the results to data/storage_units.json for the dashboard to consume.

Usage:
    Set your API key first:
        $env:GEOAPIFY_API_KEY="your_key_here"      (PowerShell)
    Then run:
        python fetch_data.py
"""

import json
import os
import time
import requests

API_KEY = os.environ.get("GEOAPIFY_API_KEY")
if not API_KEY:
    raise SystemExit(
        "ERROR: Set the GEOAPIFY_API_KEY environment variable first.\n"
        '  $env:GEOAPIFY_API_KEY="your_key_here"'
    )

PLACES_URL = "https://api.geoapify.com/v2/places"

SF_RECT = "rect:-122.52,37.815,-122.35,37.70"

PRIMARY_CATEGORY = "commercial.storage_rental"
LIMIT = 100

OUTPUT_PATH = os.path.join("data", "storage_units.json")


def fetch_places(category):
    all_features = []
    offset = 0
    while True:
        params = {
            "categories": category,
            "filter": SF_RECT,
            "limit": LIMIT,
            "offset": offset,
            "apiKey": API_KEY,
        }
        resp = requests.get(PLACES_URL, params=params, timeout=30)
        if resp.status_code != 200:
            print(f"  Request failed: HTTP {resp.status_code} - {resp.text[:200]}")
            break

        data = resp.json()
        features = data.get("features", [])
        all_features.extend(features)
        print(f"  Fetched {len(features)} (offset {offset}), total so far: {len(all_features)}")

        if len(features) < LIMIT:
            break
        offset += LIMIT
        time.sleep(0.2)

    return all_features


def build_address(props):
    parts = []
    if props.get("address_line1"):
        parts.append(props["address_line1"])
    if props.get("address_line2"):
        parts.append(props["address_line2"])
    if parts:
        return ", ".join(parts)
    return props.get("formatted")


def main():
    print(f"Querying Geoapify Places API for category '{PRIMARY_CATEGORY}' in San Francisco...")
    features = fetch_places(PRIMARY_CATEGORY)

    if not features:
        print("No results for the specific category, trying broader commercial category...")
        broad_features = fetch_places("commercial")
        features = [
            f for f in broad_features
            if "storage" in (f.get("properties", {}).get("name") or "").lower()
        ]
        print(f"  Found {len(features)} commercial places with storage in the name.")

    facilities = []
    for f in features:
        props = f.get("properties", {})
        name = props.get("name")
        if not name:
            continue

        coords = f.get("geometry", {}).get("coordinates", [None, None])
        lng, lat = coords[0], coords[1]
        if lat is None or lng is None:
            continue

        facility = {
            "place_id": props.get("place_id"),
            "name": name,
            "address": build_address(props),
            "lat": lat,
            "lng": lng,
            "phone": props.get("contact", {}).get("phone") if props.get("contact") else None,
            "website": props.get("website"),
            "opening_hours": props.get("opening_hours"),
            "brand": props.get("brand"),
            "operator": props.get("operator"),
        }
        facilities.append(facility)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(facilities, f, indent=2)

    print(f"\nSaved {len(facilities)} facilities to {OUTPUT_PATH}")
    if len(facilities) == 0:
        print("No results — try widening SF_RECT or check the category name in Geoapify docs.")


if __name__ == "__main__":
    main()
