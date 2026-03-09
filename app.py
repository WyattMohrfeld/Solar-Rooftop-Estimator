import streamlit as st
import requests

st.title("Solar Rooftop Estimator")

address = st.text_input("Enter your address")
roof_area = st.number_input("Estimated roof area (sq ft)", min_value=0)

# --- Geocoding ---
if address:
    if st.button("Look up address"):
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": address, "format": "json", "limit": 1}
        headers = {"User-Agent": "solar-rooftop-estimator"}

        response = requests.get(url, params=params, headers=headers)
        results = response.json()

        if results:
            lat = float(results[0]["lat"])
            lon = float(results[0]["lon"])
            display_name = results[0]["display_name"]
            st.success(f"📍 Found: {display_name}")
            st.write(f"Latitude: **{lat}**, Longitude: **{lon}**")
            st.session_state["lat"] = lat
            st.session_state["lon"] = lon
        else:
            st.error("Address not found. Try being more specific.")

# --- Solar Estimate ---
if roof_area > 0:
    watts_per_sqft = 18
    system_kw = (roof_area * watts_per_sqft) / 1000
    low_cost = system_kw * 2500
    high_cost = system_kw * 4000
    st.write(f"Estimated system size: **{system_kw:.2f} kW**")
    st.write(f"Estimated installed cost: **${low_cost:,.0f} – ${high_cost:,.0f}**")
