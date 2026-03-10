import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

st.title("Solar Rooftop Estimator")
st.caption("Powered by Google Solar API")

address = st.text_input("Enter your address")

# --- Fallback property type averages (sq ft of roof area) ---
PROPERTY_AVERAGES = {
    "Single-family house": 1500,
    "Townhouse / Row home": 900,
    "Condo / Apartment unit": 600,
    "Commercial building": 5000,
}

USABLE_ROOF_FACTOR = 0.75  # Only ~75% of roof is usable for solar

# --- Helper Functions ---

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

        nodes = {e["id"]: (e["lat"], e["lon"]) for e in elements if e["type"] == "node"}
        ways = [e for e in elements if e["type"] == "way" and "tags" in e]

        if not ways:
            return None

        way = ways[0]
        node_ids = way.get("nodes", [])
        coords = [nodes[n] for n in node_ids if n in nodes]

        if len(coords) < 3:
            return None

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

def get_solar_data(lat, lon):
    """Call Google Solar API for roof insights."""
    url = "https://solar.googleapis.com/v1/buildingInsights:findClosest"
    params = {
        "location.latitude": lat,
        "location.longitude": lon,
        "requiredQuality": "LOW",
        "key": GOOGLE_API_KEY,
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

# --- Main App Logic ---
if address:
    if st.button("Estimate Solar Potential"):

        # Step 1: Geocode
        with st.spinner("Looking up address..."):
            lat, lon, display_name = get_coordinates(address)

        if lat is None:
            st.error("Address not found. Try being more specific.")
        else:
            st.success(f"📍 {display_name}")
            st.write(f"Latitude: **{lat}**, Longitude: **{lon}**")

            # Step 2: Google Solar API
            solar_data = None
            usable_area = None

            if GOOGLE_API_KEY:
                with st.spinner("Fetching solar data from Google..."):
                    solar_data = get_solar_data(lat, lon)

            # Step 3: Parse Google Solar data if available
            if solar_data:
                roof_stats = solar_data.get("solarPotential", {})
                max_panels = roof_stats.get("maxArrayPanelsCount", None)
                max_area_m2 = roof_stats.get("maxArrayAreaMeters2", None)
                total_roof_m2 = roof_stats.get("wholeRoofStats", {}).get("areaMeters2", None)
                yearly_sunshine = roof_stats.get("maxSunshineHoursPerYear", None)

                # Get roof segments and find south-facing ones
                segments = roof_stats.get("roofSegmentStats", [])
                south_facing = [
                    s for s in segments
                    if abs(s.get("azimuthDegrees", 180) - 180) <= 45
                ]

                south_area_m2 = sum(s.get("stats", {}).get("areaMeters2", 0) for s in south_facing)
                south_area_sqft = round(south_area_m2 * 10.7639)
                total_usable_sqft = round(max_area_m2 * 10.7639) if max_area_m2 else None
                total_roof_sqft = round(total_roof_m2 * 10.7639) if total_roof_m2 else None

                st.divider()
                st.subheader("🛰️ Google Solar Roof Analysis")

                if total_roof_sqft:
                    st.info(f"🏠 Total roof area: **{total_roof_sqft:,} sq ft**")
                if total_usable_sqft:
                    st.info(f"☀️ Total usable solar area: **{total_usable_sqft:,} sq ft**")
                if south_area_sqft:
                    st.info(f"🧭 South-facing roof area: **{south_area_sqft:,} sq ft** *(optimal for solar)*")
                if max_panels:
                    st.write(f"Maximum panels that fit: **{max_panels} panels**")
                if yearly_sunshine:
                    st.write(f"Peak sunshine hours per year: **{yearly_sunshine:,.0f} hrs**")

                usable_area = south_area_sqft if south_area_sqft else total_usable_sqft

            else:
                # Fall back to OSM if Google Solar fails
                st.warning("⚠️ Google Solar data unavailable for this address. Falling back to OpenStreetMap.")
                with st.spinner("Looking up building footprint..."):
                    roof_area = get_building_area(lat, lon)

                if roof_area:
                    st.info(f"🏠 Building footprint found: **{roof_area:,} sq ft** (via OpenStreetMap)")
                else:
                    st.warning("⚠️ Couldn't auto-detect building size. Please select your property type:")
                    property_type = st.selectbox("Property type", list(PROPERTY_AVERAGES.keys()))
                    roof_area = PROPERTY_AVERAGES[property_type]
                    st.info(f"Using average roof area for {property_type}: **{roof_area:,} sq ft**")

                usable_area = roof_area * USABLE_ROOF_FACTOR

            # Step 4: Solar cost estimate
            if usable_area:
                watts_per_sqft = 18
                system_kw = (usable_area * watts_per_sqft) / 1000
                low_cost = system_kw * 2500
                high_cost = system_kw * 4000

                st.divider()
                st.subheader("💰 Cost Estimate")
                st.write(f"Usable roof area for estimate: **{usable_area:,.0f} sq ft**")
                st.write(f"Estimated system size: **{system_kw:.2f} kW**")
                st.write(f"Estimated installed cost: **${low_cost:,.0f} – ${high_cost:,.0f}**")
                st.caption("Cost estimate based on $2.50–$4.00 per watt, which is the current U.S. industry average.")

            # Step 5: Coming soon heatmap
            st.divider()
            st.subheader("🗺️ Solar Flux Heatmap")
            st.info("🚧 **Coming Soon** — A roof-level heatmap showing sun exposure across every part of your roof, so you can see exactly where panels will perform best.")
