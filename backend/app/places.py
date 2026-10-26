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
        "displayName": {
            "languageCode": "en",
            "text": "The TOP"
        },
        "formattedAddress": "30 N Main St, Gainesville, FL 32601, USA",
        "id": "ChIJ2-LhlIyj6IgRQ8m7dbD2M2I",
        "location": {
            "latitude": 29.652562399999994,
            "longitude": -82.3252783
        }
    },
    {
        "displayName": {
            "languageCode": "en",
            "text": "Mom's OG"
        },
        "formattedAddress": "1017 W University Ave, Gainesville, FL 32601, USA",
        "id": "ChIJmZH-14Kj6IgR_cTSYvvHbfg",
        "location": {
            "latitude": 29.6518473,
            "longitude": -82.33580979999999
        }
    },
    {
        "displayName": {
            "languageCode": "en",
            "text": "Tela Latin Grill"
        },
        "formattedAddress": "1702 W University Ave, Gainesville, FL 32603, USA",
        "id": "ChIJ4Yr9ZGaj6IgRZoHpvEn3RSE",
        "location": {
            "latitude": 29.652417900000003,
            "longitude": -82.345129
        }
    },
    {
        "displayName": {
            "languageCode": "en",
            "text": "BITE of POWER"
        },
        "formattedAddress": "Inside of Target Copy/Dunkin Donuts/Sushi2go, 1412 W University Ave Ste c, Gainesville, FL 32603, USA",
        "id": "ChIJTQUJw-ej6IgRFbKLU-Vidp8",
        "location": {
            "latitude": 29.6522253,
            "longitude": -82.3412152
        }
    },
    {
        "displayName": {
            "languageCode": "en",
            "text": "The Dunbar"
        },
        "formattedAddress": "732 NW 4th St, Gainesville, FL 32601, USA",
        "id": "ChIJl-EDM7Oj6IgR9TfspMN0vAY",
        "location": {
            "latitude": 29.6588477,
            "longitude": -82.3289583
    }
    }
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