from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import requests
app = Flask(__name__) #flask object!
load_dotenv() #loads API key

demo_status = True

if demo_status:
    PLACES_API_KEY = "testing"
else:
    PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
    #actual API key, only use when NEEDED)

places_url = "https://places.googleapis.com/v1/places:searchText"

@app.route("/api/health", methods = ["GET"])
def health_status():
    return {"status": "LOOP backend up and running"}

@app.route("/api/places/search", methods = ["GET"])
def search():
    query = request.args.get("query", "").strip()

    if not query:
        return jsonify({"error": "Query required"}), 400 #client error code
    if not PLACES_API_KEY:
        return jsonify({"error": "Google API key is missing"}), 500 #server error code
    elif PLACES_API_KEY == "testing":
        #placeholder for potential db implementation of cached data
        return jsonify({"msg": "we're still testing!"})

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": PLACES_API_KEY,
        "X-Goog-FieldMask": (
            "places.id,"
            "places.displayName,"
            "places.formattedAddress,"
            "places.location"
        )
    }
    body = {
        "textQuery": query,
        "maxResultCount": 5
    }
    try:
        #attempting API get request
        response = requests.post(places_url, headers = headers, json = body, timeout = 5)
        if response.ok:
            data = response.json()
            return jsonify({"places": data.get("places", [])})
        else:
            app.logger.error("Places request failed %s", response.status_code)
            print("uhhh couldn't search")
            return jsonify({"error": "Search failed"}), 500

    except requests.RequestException:
        app.logger.exception("Unable to connect to Places")
        print("uhhh couldn't connect to places")
        return jsonify({"error": "unable to connect to places"}), 500
@app.route('/')
def index():
    return "herro!"

if __name__ == "__main__":
    app.run(debug = True)