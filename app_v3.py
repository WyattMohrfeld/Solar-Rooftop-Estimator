import streamlit as st
import requests
import os
import plotly.graph_objects as go
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

st.set_page_config(
    page_title="Solar Rooftop Estimator",
    page_icon="☀️",
    layout="centered"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display&display=swap');

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

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
    .hero-subtitle { color: #888; font-size: 1rem; font-weight: 300; margin-bottom: 2rem; }
    .section-header {
        font-family: 'DM Serif Display', serif;
        font-size: 1.4rem;
        color: #f5a623;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .stat-row { display: flex; flex-direction: column; gap: 0.6rem; margin-bottom: 1rem; }
    .stat-line {
        display: flex; justify-content: space-between; align-items: center;
        padding: 0.65rem 1rem; background: #1a1a2e;
        border-radius: 8px; border-left: 3px solid #f5a623;
    }
    .stat-label { color: #aaa; font-size: 0.9rem; font-weight: 400; }
    .stat-value { color: #fff; font-size: 1rem; font-weight: 600; }
    .valuation-box { background: #1a1a2e; border-radius: 12px; padding: 1.2rem 1.4rem; margin-bottom: 0.8rem; }
    .valuation-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: #888; margin-bottom: 0.3rem; }
    .valuation-mohrfeld { font-family: 'DM Serif Display', serif; font-size: 2rem; color: #f5a623; }
    .valuation-market { font-family: 'DM Serif Display', serif; font-size: 2rem; color: #ccc; }
    .valuation-desc { font-size: 0.8rem; color: #666; margin-top: 0.2rem; }
    .savings-tag {
        display: inline-block; background: #0d2e1a; color: #2ecc71;
        border-radius: 20px; padding: 0.2rem 0.8rem;
        font-size: 0.8rem; font-weight: 600; margin-top: 0.5rem;
    }
    .savings-card {
        background: #0d2e1a; border-radius: 12px;
        padding: 1.2rem 1.4rem; margin-bottom: 0.8rem;
        border-left: 3px solid #2ecc71;
    }
    .savings-card-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: #2ecc71; margin-bottom: 0.3rem; }
    .savings-card-val { font-family: 'DM Serif Display', serif; font-size: 2rem; color: #2ecc71; }
    .savings-card-sub { font-size: 0.8rem; color: #5a8f6f; margin-top: 0.2rem; }
    .payback-section { margin-top: 0.5rem; }
    .payback-label { font-size: 0.8rem; color: #888; margin-bottom: 0.4rem; }
    .payback-bar-bg { background: #1a1a2e; border-radius: 6px; height: 10px; width: 100%; overflow: hidden; margin-bottom: 0.3rem; }
    .payback-bar-fill { height: 100%; border-radius: 6px; background: linear-gradient(90deg, #2ecc71, #f5a623); }
    .payback-note { font-size: 0.75rem; color: #666; }
    .coming-soon-box {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px dashed #f5a623; border-radius: 12px;
        padding: 2rem; text-align: center; margin-top: 1rem;
    }
    .coming-soon-box h3 { color: #f5a623; font-family: 'DM Serif Display', serif; font-size: 1.3rem; margin-bottom: 0.5rem; }
    .coming-soon-box p { color: #888; font-size: 0.9rem; }
    .stButton > button {
        background: linear-gradient(135deg, #f5a623, #f7c948);
        color: #0f1117; font-weight: 600; font-family: 'DM Sans', sans-serif;
        border: none; border-radius: 8px; padding: 0.6rem 2rem;
        font-size: 1rem; width: 100%; transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.85; color: #0f1117; }
    .stTextInput > div > div > input {
        background: #1a1a2e; border: 1px solid #2a2a4e;
        border-radius: 8px; color: #fff; font-family: 'DM Sans', sans-serif;
    }
    hr { border-color: #2a2a4e !important; margin: 1.5rem 0 !important; }
    .disclaimer { font-size: 0.75rem; color: #555; margin-top: 1rem; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

# --- State utility rates and sun hours ---
STATE_DATA = {
    "AL": ("Alabama", 0.137, 4.7), "AK": ("Alaska", 0.231, 3.8), "AZ": ("Arizona", 0.126, 6.5),
    "AR": ("Arkansas", 0.102, 4.9), "CA": ("California", 0.255, 5.9), "CO": ("Colorado", 0.128, 5.5),
    "CT": ("Connecticut", 0.238, 4.3), "DE": ("Delaware", 0.137, 4.5), "FL": ("Florida", 0.129, 5.5),
    "GA": ("Georgia", 0.122, 5.2), "HI": ("Hawaii", 0.384, 5.8), "ID": ("Idaho", 0.102, 5.0),
    "IL": ("Illinois", 0.143, 4.6), "IN": ("Indiana", 0.129, 4.6), "IA": ("Iowa", 0.116, 4.7),
    "KS": ("Kansas", 0.125, 5.3), "KY": ("Kentucky", 0.116, 4.6), "LA": ("Louisiana", 0.110, 5.1),
    "ME": ("Maine", 0.228, 4.4), "MD": ("Maryland", 0.148, 4.6), "MA": ("Massachusetts", 0.250, 4.5),
    "MI": ("Michigan", 0.175, 4.4), "MN": ("Minnesota", 0.138, 4.7), "MS": ("Mississippi", 0.118, 5.0),
    "MO": ("Missouri", 0.115, 4.8), "MT": ("Montana", 0.120, 5.1), "NE": ("Nebraska", 0.113, 5.0),
    "NV": ("Nevada", 0.120, 6.4), "NH": ("New Hampshire", 0.220, 4.4), "NJ": ("New Jersey", 0.171, 4.6),
    "NM": ("New Mexico", 0.127, 6.8), "NY": ("New York", 0.208, 4.5), "NC": ("North Carolina", 0.114, 5.0),
    "ND": ("North Dakota", 0.108, 4.7), "OH": ("Ohio", 0.138, 4.5), "OK": ("Oklahoma", 0.118, 5.4),
    "OR": ("Oregon", 0.117, 4.7), "PA": ("Pennsylvania", 0.147, 4.5), "RI": ("Rhode Island", 0.240, 4.4),
    "SC": ("South Carolina", 0.124, 5.1), "SD": ("South Dakota", 0.120, 5.0), "TN": ("Tennessee", 0.114, 4.8),
    "TX": ("Texas", 0.128, 5.7), "UT": ("Utah", 0.109, 6.0), "VT": ("Vermont", 0.208, 4.4),
    "VA": ("Virginia", 0.131, 4.7), "WA": ("Washington", 0.103, 4.3), "WV": ("West Virginia", 0.122, 4.4),
    "WI": ("Wisconsin", 0.158, 4.5), "WY": ("Wyoming", 0.118, 5.2)
}

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

def get_state_from_address(display_name):
    """Extract US state abbreviation from Nominatim display name."""
    state_names = {v[0]: k for k, v in STATE_DATA.items()}
    parts = [p.strip() for p in display_name.split(",")]
    for part in parts:
        if part in STATE_DATA:
            return part
        if part in state_names:
            return state_names[part]
    return "CA"  # default fallback

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

def render_savings_section(system_kw, state_code, mohrfeld_cost, monthly_bill_override=None):
    """Render the savings + payback + production section given system size and state."""
    state_name, rate, sun_hrs = STATE_DATA.get(state_code, ("California", 0.255, 5.9))

    annual_kwh = system_kw * sun_hrs * 365 * 0.97
    annual_savings = annual_kwh * rate
    monthly_savings = annual_savings / 12
    net_cost = mohrfeld_cost * 0.70  # 30% federal ITC
    payback_yrs = net_cost / annual_savings if annual_savings > 0 else 99
    lifetime_savings = (annual_savings * 25) - net_cost

    # Avg US home uses ~10,500 kWh/yr; estimate bill coverage
    avg_home_kwh = 10_500
    bill_coverage_pct = min(round(annual_kwh / avg_home_kwh * 100), 100)

    st.markdown("---")
    st.markdown('<div class="section-header">💡 Energy Production & Savings</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="stat-line" style="margin-bottom:0.75rem;">
        <span class="stat-label">State detected: {state_name}</span>
        <span class="stat-value">{rate*100:.1f}¢/kWh · {sun_hrs} peak sun hrs/day</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Energy production stat cards ──────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="savings-card">
            <div class="savings-card-label">Annual Energy Production</div>
            <div class="savings-card-val">{annual_kwh:,.0f} kWh</div>
            <div class="savings-card-sub">estimated year 1 output</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="savings-card">
            <div class="savings-card-label">% of Home Bill Covered</div>
            <div class="savings-card-val">{bill_coverage_pct}%</div>
            <div class="savings-card-sub">based on avg U.S. home usage</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Monthly / annual savings cards ───────────────────────────────────────
    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f"""
        <div class="savings-card">
            <div class="savings-card-label">Monthly Savings (est.)</div>
            <div class="savings-card-val">${monthly_savings:,.0f}</div>
            <div class="savings-card-sub">offset on your electricity bill</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="savings-card">
            <div class="savings-card-label">Annual Savings (est.)</div>
            <div class="savings-card-val">${annual_savings:,.0f}</div>
            <div class="savings-card-sub">first year at current rates</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Payback bar ───────────────────────────────────────────────────────────
    pct = min(payback_yrs / 25 * 100, 100)
    payback_str = f"{payback_yrs:.1f} years" if payback_yrs < 25 else "25+ years"
    lifetime_str = f"${lifetime_savings:,.0f}" if lifetime_savings > 0 else "—"

    st.markdown(f"""
    <div class="valuation-box payback-section">
        <div class="valuation-label">Payback Period (after 30% federal ITC)</div>
        <div class="valuation-mohrfeld">{payback_str}</div>
        <div class="payback-bar-bg" style="margin-top:0.6rem;">
            <div class="payback-bar-fill" style="width:{pct:.1f}%;"></div>
        </div>
        <div class="payback-note">
            Break-even at year {payback_str} &nbsp;·&nbsp; 25-yr system life
            &nbsp;·&nbsp; Lifetime net savings: <strong style="color:#2ecc71;">{lifetime_str}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 25-year cumulative savings chart ──────────────────────────────────────
    st.markdown('<div class="section-header">📈 25-Year Savings Projection</div>', unsafe_allow_html=True)

    years = list(range(0, 26))
    degradation = 0.005  # 0.5%/yr panel degradation
    utility_inflation = 0.03  # 3%/yr electricity rate increase

    cumulative = []
    running = -net_cost  # start negative (what you paid after ITC)
    for yr in years:
        if yr == 0:
            cumulative.append(round(running))
        else:
            yr_production = annual_kwh * ((1 - degradation) ** yr)
            yr_rate = rate * ((1 + utility_inflation) ** yr)
            yr_savings = yr_production * yr_rate
            running += yr_savings
            cumulative.append(round(running))

    breakeven_yr = next((y for y, v in zip(years, cumulative) if v >= 0), None)

    fig = go.Figure()

    # Shaded loss zone (below zero)
    loss_x = [y for y, v in zip(years, cumulative) if v <= 0]
    loss_y = [v for v in cumulative if v <= 0]
    if loss_x:
        fig.add_trace(go.Scatter(
            x=loss_x + loss_x[::-1],
            y=loss_y + [0] * len(loss_y),
            fill='toself',
            fillcolor='rgba(231,76,60,0.12)',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))

    # Shaded gain zone (above zero)
    gain_x = [y for y, v in zip(years, cumulative) if v >= 0]
    gain_y = [v for v in cumulative if v >= 0]
    if gain_x:
        fig.add_trace(go.Scatter(
            x=gain_x + gain_x[::-1],
            y=gain_y + [0] * len(gain_y),
            fill='toself',
            fillcolor='rgba(46,204,113,0.12)',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))

    # Main cumulative savings line
    fig.add_trace(go.Scatter(
        x=years,
        y=cumulative,
        mode='lines',
        name='Cumulative savings',
        line=dict(color='#f5a623', width=3),
        hovertemplate='Year %{x}<br><b>%{customdata}</b><extra></extra>',
        customdata=[f"${v:,.0f}" if v >= 0 else f"-${abs(v):,.0f}" for v in cumulative]
    ))

    # Zero line
    fig.add_hline(y=0, line_dash='dash', line_color='#444', line_width=1)

    # Breakeven annotation
    if breakeven_yr is not None:
        fig.add_vline(x=breakeven_yr, line_dash='dot', line_color='#2ecc71', line_width=1.5)
        fig.add_annotation(
            x=breakeven_yr, y=max(cumulative) * 0.85,
            text=f"Break-even<br>Year {breakeven_yr}",
            showarrow=False,
            font=dict(color='#2ecc71', size=12),
            bgcolor='rgba(13,46,26,0.7)',
            borderpad=6,
        )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='#0f1117',
        font=dict(family='DM Sans', color='#aaa', size=12),
        margin=dict(l=10, r=10, t=10, b=10),
        height=320,
        xaxis=dict(
            title='Year',
            gridcolor='#1a1a2e',
            tickmode='linear', dtick=5,
            color='#666',
        ),
        yaxis=dict(
            title='Cumulative $ savings',
            gridcolor='#1a1a2e',
            color='#666',
            tickprefix='$',
            tickformat=',.0f',
        ),
        showlegend=False,
        hovermode='x unified',
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
    <div class="disclaimer">
        Production estimates use {state_name} avg utility rate ({rate*100:.1f}¢/kWh), {sun_hrs} peak sun hrs/day,
        0.97 system efficiency, 0.5%/yr panel degradation, and 3%/yr electricity rate inflation.
        Net cost reflects 30% federal ITC. Bill coverage based on avg U.S. home usage of 10,500 kWh/yr.
        Actual results vary based on net metering policy, roof orientation, shading, and local incentives.
    </div>
    """, unsafe_allow_html=True)


# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">☀️ Solar Rooftop Estimator</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Enter any address to get an instant solar potential analysis, cost estimate, and savings projection.</div>', unsafe_allow_html=True)

address = st.text_input("", placeholder="e.g. 123 Main St, Santa Cruz, CA")

if address:
    if st.button("⚡ Estimate Solar Potential"):

        with st.spinner("Looking up address..."):
            lat, lon, display_name = get_coordinates(address)

        if lat is None:
            st.error("Address not found. Try being more specific.")
        else:
            st.success(f"📍 {display_name}")
            state_code = get_state_from_address(display_name)

            solar_data = None
            usable_area = None

            if GOOGLE_API_KEY:
                with st.spinner("Fetching solar data from Google..."):
                    solar_data = get_solar_data(lat, lon)

            # ── Roof Analysis ──────────────────────────────────────────────
            if solar_data:
                roof_stats = solar_data.get("solarPotential", {})
                max_panels = roof_stats.get("maxArrayPanelsCount", None)
                max_area_m2 = roof_stats.get("maxArrayAreaMeters2", None)
                total_roof_m2 = roof_stats.get("wholeRoofStats", {}).get("areaMeters2", None)
                yearly_sunshine = roof_stats.get("maxSunshineHoursPerYear", None)

                segments = roof_stats.get("roofSegmentStats", [])
                south_facing = [s for s in segments if abs(s.get("azimuthDegrees", 180) - 180) <= 45]
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

            # ── Cost Estimate ──────────────────────────────────────────────
            if usable_area:
                system_kw = (usable_area * 18) / 1000
                mohrfeld_cost = system_kw * 2500
                market_cost = system_kw * 4000
                savings = market_cost - mohrfeld_cost

                st.markdown("---")
                st.markdown('<div class="section-header">💰 Cost Estimate</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="stat-line" style="margin-bottom:1rem;"><span class="stat-label">Estimated System Size</span><span class="stat-value">{system_kw:.1f} kW</span></div>',
                    unsafe_allow_html=True
                )

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

                # ── Savings & Payback (NEW) ────────────────────────────────
                render_savings_section(system_kw, state_code, mohrfeld_cost)

            # ── Coming Soon Heatmap ────────────────────────────────────────
            st.markdown("---")
            st.markdown("""
            <div class="coming-soon-box">
                <h3>🗺️ Solar Flux Heatmap — Coming Soon</h3>
                <p>A roof-level heatmap showing sun exposure across every part of your roof,<br>
                so you can see exactly where panels will perform best.</p>
            </div>
            """, unsafe_allow_html=True)
