"""
Places search proxy.
Based on backend_flask.py, moved into a Blueprint so it runs
inside create_app (flask run and the tests only use that factory).
"""
import os

import requests
from flask import Blueprint, jsonify, request

places_bp = Blueprint("places", __name__)

# Placeholder while caching is figured out: when True,
# return mock data and never call Google.
demo_status = True

MOCK_PLACES = [
    {
        "id": "mock-1",
        "name": "Sample Coffee Shop",
        "address": "123 Main St, Gainesville, FL",
        "location": {"lat": 29.6516, "lng": -82.3248},
    },
    {
        "id": "mock-2",
        "name": "Sample Park",
        "address": "456 Park Ave, Gainesville, FL",
        "location": {"lat": 29.6436, "lng": -82.3549},
    },
]


@places_bp.get("/search")
def search_places():
    query = (request.args.get("query") or "").strip()
    if not query:
        return jsonify({"error": "bad_request", "message": "Query required"}), 400

    if demo_status:
        return jsonify({"places": MOCK_PLACES})

    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    if not api_key:
        return jsonify({"error": "server_error", "message": "Places API key not set"}), 500

    try:
        resp = requests.post(
            "https://places.googleapis.com/v1/places:searchText",
            headers={
                "X-Goog-Api-Key": api_key,
                "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location",
            },
            json={"textQuery": query, "maxResultCount": 5},
            timeout=5,
        )
        resp.raise_for_status()
    except requests.RequestException:
        return jsonify({"error": "bad_gateway", "message": "Places lookup failed"}), 502

    places = [
        {
            "id": p.get("id"),
            "name": (p.get("displayName") or {}).get("text"),
            "address": p.get("formattedAddress"),
            "location": {
                "lat": (p.get("location") or {}).get("latitude"),
                "lng": (p.get("location") or {}).get("longitude"),
            },
        }
        for p in resp.json().get("places", [])
    ]
    return jsonify({"places": places})