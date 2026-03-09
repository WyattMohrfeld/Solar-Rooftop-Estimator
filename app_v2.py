import streamlit as st
import requests

st.title("Solar Rooftop Estimator")

address = st.text_input("Enter your address")

# --- Fallback property type averages (sq ft of roof area) ---
PROPERTY_AVERAGES = {
    "Single-family house": 1500,
    "Townhouse / Row home": 900,
    "Condo / Apartment unit": 600,
    "Commercial building": 5000,
}

def get_coordinates(address):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json", "limit": 1}
    headers = {"User-Agent": "solar-rooftop-estimator"}
    response = requests.get(url, params=params, headers=headers)
    results = response.json()
    if results:
        return float(results[0]["lat"]), float(results[0]["lon"]), results[0]["display_name"]
    return None, None, None

def get_building_area(lat, lon):
    """Query OSM Overpass API for building footprint near the given coordinates."""
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    way(around:30,{lat},{lon})[building];
    out body;
    >;
    out skel qt;
    """
    try:
        response = requests.post(overpass_url, data=query, timeout=10)
        data = response.json()
        elements = data.get("elements", [])

        # Find nodes and ways
        nodes = {e["id"]: (e["lat"], e["lon"]) for e in elements if e["type"] == "node"}
        ways = [e for e in elements if e["type"] == "way" and "tags" in e]

        if not ways:
            return None

        # Use the first building way found
        way = ways[0]
        node_ids = way.get("nodes", [])
        coords = [nodes[n] for n in node_ids if n in nodes]

        if len(coords) < 3:
            return None

        # Calculate polygon area using Shoelace formula (in degrees, then convert to sq ft)
        def shoelace(pts):
            n = len(pts)
            area = 0
            for i in range(n):
                j = (i + 1) % n
                area += pts[i][0] * pts[j][1]
                area -= pts[j][0] * pts[i][1]
            return abs(area) / 2

        area_deg = shoelace(coords)
        # Convert from degrees² to meters² (approximate at mid-latitudes)
        area_m2 = area_deg * (111_320 ** 2) * abs(0.7)  # ~cos(45°) correction
        area_sqft = area_m2 * 10.7639

        return round(area_sqft)

    except Exception:
        return None

# --- Main App Logic ---
if address:
    if st.button("Estimate Solar Potential"):
        with st.spinner("Looking up address..."):
            lat, lon, display_name = get_coordinates(address)

        if lat is None:
            st.error("Address not found. Try being more specific.")
        else:
            st.success(f"📍 {display_name}")
            st.write(f"Latitude: **{lat}**, Longitude: **{lon}**")

            with st.spinner("Looking up building footprint..."):
                roof_area = get_building_area(lat, lon)

            if roof_area:
                st.info(f"🏠 Building footprint found: **{roof_area:,} sq ft** (via OpenStreetMap)")
            else:
                st.warning("⚠️ Couldn't auto-detect building size. Please select your property type:")
                property_type = st.selectbox("Property type", list(PROPERTY_AVERAGES.keys()))
                roof_area = PROPERTY_AVERAGES[property_type]
                st.info(f"Using average roof area for {property_type}: **{roof_area:,} sq ft**")

            # --- Solar Estimate ---
            if roof_area:
                watts_per_sqft = 18
                system_kw = (roof_area * watts_per_sqft) / 1000
                low_cost = system_kw * 2500
                high_cost = system_kw * 4000

                st.divider()
                st.subheader("☀️ Solar Estimate")
                st.write(f"Estimated system size: **{system_kw:.2f} kW**")
                st.write(f"Estimated installed cost: **${low_cost:,.0f} – ${high_cost:,.0f}**")
