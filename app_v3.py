import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- Page Config ---
st.set_page_config(
    page_title="Solar Rooftop Estimator",
    page_icon="☀️",
    layout="centered"
)

# --- Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .hero-title {
        font-family: 'DM Serif Display', serif;
        font-size: 3rem;
        background: linear-gradient(135deg, #f5a623, #f7c948, #fff5d6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.2rem;
        line-height: 1.1;
    }

    .hero-subtitle {
        color: #888;
        font-size: 1rem;
        font-weight: 300;
        margin-bottom: 2rem;
    }

    .section-header {
        font-family: 'DM Serif Display', serif;
        font-size: 1.4rem;
        color: #f5a623;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }

    .stat-row {
        display: flex;
        flex-direction: column;
        gap: 0.6rem;
        margin-bottom: 1rem;
    }

    .stat-line {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.65rem 1rem;
        background: #1a1a2e;
        border-radius: 8px;
        border-left: 3px solid #f5a623;
    }

    .stat-label {
        color: #aaa;
        font-size: 0.9rem;
        font-weight: 400;
    }

    .stat-value {
        color: #fff;
        font-size: 1rem;
        font-weight: 600;
    }

    .valuation-box {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 0.8rem;
    }

    .valuation-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #888;
        margin-bottom: 0.3rem;
    }

    .valuation-mohrfeld {
        font-family: 'DM Serif Display', serif;
        font-size: 2rem;
        color: #f5a623;
    }

    .valuation-market {
        font-family: 'DM Serif Display', serif;
        font-size: 2rem;
        color: #ccc;
    }

    .valuation-desc {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.2rem;
    }

    .savings-tag {
        display: inline-block;
        background: #0d2e1a;
        color: #2ecc71;
        border-radius: 20px;
        padding: 0.2rem 0.8rem;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }

    .coming-soon-box {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px dashed #f5a623;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        margin-top: 1rem;
    }

    .coming-soon-box h3 {
        color: #f5a623;
        font-family: 'DM Serif Display', serif;
        font-size: 1.3rem;
        margin-bottom: 0.5rem;
    }

    .coming-soon-box p {
        color: #888;
        font-size: 0.9rem;
    }

    .stButton > button {
        background: linear-gradient(135deg, #f5a623, #f7c948);
        color: #0f1117;
        font-weight: 600;
        font-family: 'DM Sans', sans-serif;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        font-size: 1rem;
        width: 100%;
        transition: opacity 0.2s;
    }

    .stButton > button:hover {
        opacity: 0.85;
        color: #0f1117;
    }

    .stTextInput > div > div > input {
        background: #1a1a2e;
        border: 1px solid #2a2a4e;
        border-radius: 8px;
        color: #fff;
        font-family: 'DM Sans', sans-serif;
    }

    hr {
        border-color: #2a2a4e !important;
        margin: 1.5rem 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="hero-title">☀️ Solar Rooftop Estimator</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Enter any address to get an instant solar potential analysis and cost estimate.</div>', unsafe_allow_html=True)

# --- Constants ---
PROPERTY_AVERAGES = {
    "Single-family house": 1500,
    "Townhouse / Row home": 900,
    "Condo / Apartment unit": 600,
    "Commercial building": 5000,
}
USABLE_ROOF_FACTOR = 0.75

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
        coords = [nodes[n] for n in way.get("nodes", []) if n in nodes]
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

        area_m2 = shoelace(coords) * (111_320 ** 2) * 0.7
        return round(area_m2 * 10.7639)
    except Exception:
        return None

def get_solar_data(lat, lon):
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

# --- Main App ---
address = st.text_input("", placeholder="e.g. 123 Main St, Santa Cruz, CA")

if address:
    if st.button("⚡ Estimate Solar Potential"):

        with st.spinner("Looking up address..."):
            lat, lon, display_name = get_coordinates(address)

        if lat is None:
            st.error("Address not found. Try being more specific.")
        else:
            st.success(f"📍 {display_name}")

            solar_data = None
            usable_area = None

            if GOOGLE_API_KEY:
                with st.spinner("Fetching solar data from Google..."):
                    solar_data = get_solar_data(lat, lon)

            # --- Roof Analysis ---
            if solar_data:
                roof_stats = solar_data.get("solarPotential", {})
                max_panels = roof_stats.get("maxArrayPanelsCount", None)
                max_area_m2 = roof_stats.get("maxArrayAreaMeters2", None)
                total_roof_m2 = roof_stats.get("wholeRoofStats", {}).get("areaMeters2", None)
                yearly_sunshine = roof_stats.get("maxSunshineHoursPerYear", None)

                segments = roof_stats.get("roofSegmentStats", [])
                south_facing = [
                    s for s in segments
                    if abs(s.get("azimuthDegrees", 180) - 180) <= 45
                ]
                south_area_sqft = round(sum(
                    s.get("stats", {}).get("areaMeters2", 0) for s in south_facing
                ) * 10.7639)
                total_usable_sqft = round(max_area_m2 * 10.7639) if max_area_m2 else None
                total_roof_sqft = round(total_roof_m2 * 10.7639) if total_roof_m2 else None
                usable_area = south_area_sqft if south_area_sqft else total_usable_sqft

                st.markdown("---")
                st.markdown('<div class="section-header">🛰️ Roof Analysis</div>', unsafe_allow_html=True)

                stats = []
                if total_roof_sqft:
                    stats.append(("Total Roof Area", f"{total_roof_sqft:,} sq ft"))
                if total_usable_sqft:
                    stats.append(("Usable Solar Area", f"{total_usable_sqft:,} sq ft"))
                if south_area_sqft:
                    stats.append(("South-Facing Area ✦ optimal", f"{south_area_sqft:,} sq ft"))
                if max_panels:
                    stats.append(("Max Panels", f"{max_panels} panels"))
                if yearly_sunshine:
                    stats.append(("Peak Sun Hours / Year", f"{yearly_sunshine:,.0f} hrs"))

                rows_html = "".join([
                    f'<div class="stat-line"><span class="stat-label">{label}</span><span class="stat-value">{value}</span></div>'
                    for label, value in stats
                ])
                st.markdown(f'<div class="stat-row">{rows_html}</div>', unsafe_allow_html=True)

            else:
                st.warning("⚠️ Google Solar data unavailable. Falling back to OpenStreetMap.")
                with st.spinner("Looking up building footprint..."):
                    roof_area = get_building_area(lat, lon)

                if not roof_area:
                    st.warning("⚠️ Couldn't auto-detect size. Please select your property type:")
                    property_type = st.selectbox("Property type", list(PROPERTY_AVERAGES.keys()))
                    roof_area = PROPERTY_AVERAGES[property_type]

                usable_area = roof_area * USABLE_ROOF_FACTOR

            # --- Cost Estimate ---
            if usable_area:
                system_kw = (usable_area * 18) / 1000
                mohrfeld_cost = system_kw * 2500
                market_cost = system_kw * 4000
                savings = market_cost - mohrfeld_cost

                st.markdown("---")
                st.markdown('<div class="section-header">💰 Cost Estimate</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="stat-line" style="margin-bottom:1rem;"><span class="stat-label">Estimated System Size</span><span class="stat-value">{system_kw:.1f} kW</span></div>', unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class="valuation-box">
                        <div class="valuation-label">Mohrfeld Valuation</div>
                        <div class="valuation-mohrfeld">${mohrfeld_cost:,.0f}</div>
                        <div class="valuation-desc">Best-in-class pricing<br>at $2.50 / watt</div>
                        <div class="savings-tag">Save ${savings:,.0f} vs market</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="valuation-box">
                        <div class="valuation-label">Market Valuation</div>
                        <div class="valuation-market">${market_cost:,.0f}</div>
                        <div class="valuation-desc">U.S. industry average<br>at $4.00 / watt</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.caption("Estimates based on $2.50–$4.00/watt installed cost, the current U.S. industry average.")

            # --- Coming Soon Heatmap ---
            st.markdown("---")
            st.markdown("""
            <div class="coming-soon-box">
                <h3>🗺️ Solar Flux Heatmap — Coming Soon</h3>
                <p>A roof-level heatmap showing sun exposure across every part of your roof,<br>
                so you can see exactly where panels will perform best.</p>
            </div>
            """, unsafe_allow_html=True)
