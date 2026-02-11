import streamlit as st

st.title("Solar Rooftop Estimator")

address = st.text_input("Enter your address")
roof_area = st.number_input("Estimated roof area (sq ft)", min_value=0)

if roof_area > 0:
    watts_per_sqft = 18
    system_kw = (roof_area * watts_per_sqft) / 1000
    low_cost = system_kw * 2500
    high_cost = system_kw * 4000

    st.write(f"Estimated system size: **{system_kw:.2f} kW**")
    st.write(f"Estimated installed cost: **${low_cost:,.0f} – ${high_cost:,.0f}**")



