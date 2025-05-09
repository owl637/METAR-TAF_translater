import os
import json

file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'icao_locations.json')
with open(file_path, 'r', encoding='utf-8') as f:
    ICAO_LOCATIONS = json.load(f)

def extract_icao(code):
    tokens = code.strip().split()
    if tokens[0].upper() == "TAF":
          if tokens[1].upper() == "TAF":
              tokens.pop(0)
              tokens.pop(0)
          else:
              tokens.pop(0)
    return tokens[0].upper()

def get_google_maps_url(icao_code):
    loc = ICAO_LOCATIONS.get(icao_code)
    if loc:
        lat, lon = loc["lat"], loc["lon"]
        return f"https://maps.google.com/?q={lat},{lon}"
    return None

def get_airport_name(icao_code):
    loc = ICAO_LOCATIONS.get(icao_code)
    return loc.get("name", "") if loc else ""
