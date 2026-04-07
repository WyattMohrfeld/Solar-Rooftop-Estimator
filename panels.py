import streamlit as st

st.set_page_config(
    page_title="Solar Panel Catalog",
    page_icon="🔆",
    layout="centered"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display&display=swap');

    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

    .hero-title {
        font-family: 'DM Serif Display', serif;
        font-size: 2.8rem;
        background: linear-gradient(135deg, #f5a623, #f7c948, #fff5d6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.2rem;
        line-height: 1.1;
    }
    .hero-subtitle { color: #888; font-size: 1rem; font-weight: 300; margin-bottom: 2rem; }

    .panel-card {
        background: #1a1a2e;
        border-radius: 16px;
        padding: 0;
        margin-bottom: 2rem;
        overflow: hidden;
        border: 1px solid #2a2a4e;
    }
    .panel-img-wrap {
        width: 100%;
        height: 220px;
        overflow: hidden;
        background: #0f1117;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .panel-img-wrap img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        object-position: center;
    }
    .panel-body { padding: 1.4rem 1.6rem; }
    .panel-tier {
        display: inline-block;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        margin-bottom: 0.6rem;
    }
    .tier-premium { background: #2a1f00; color: #f5a623; }
    .tier-value    { background: #0d2e1a; color: #2ecc71; }
    .tier-budget   { background: #16213e; color: #7eb3f5; }

    .panel-name {
        font-family: 'DM Serif Display', serif;
        font-size: 1.5rem;
        color: #fff;
        margin-bottom: 0.2rem;
        line-height: 1.2;
    }
    .panel-tagline { color: #888; font-size: 0.85rem; margin-bottom: 1.2rem; }

    .stats-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        margin-bottom: 1.2rem;
    }
    .stat-box {
        background: #0f1117;
        border-radius: 10px;
        padding: 0.7rem 0.5rem;
        text-align: center;
    }
    .stat-box-label { font-size: 0.65rem; color: #666; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.25rem; }
    .stat-box-val   { font-size: 1.05rem; font-weight: 600; color: #fff; }
    .stat-box-unit  { font-size: 0.65rem; color: #888; }

    .stat-box-wide {
        background: #0f1117;
        border-radius: 10px;
        padding: 0.6rem 0.8rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }
    .stat-box-wide-label { font-size: 0.8rem; color: #888; }
    .stat-box-wide-val   { font-size: 0.9rem; font-weight: 600; color: #fff; }

    .best-for {
        background: #111827;
        border-left: 3px solid #f5a623;
        border-radius: 0 8px 8px 0;
        padding: 0.6rem 0.9rem;
        margin-top: 1rem;
        font-size: 0.82rem;
        color: #aaa;
    }
    .best-for strong { color: #f5a623; }

    .divider-label {
        font-family: 'DM Serif Display', serif;
        font-size: 1.2rem;
        color: #f5a623;
        margin: 2rem 0 1rem;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid #2a2a4e;
    }
</style>
""", unsafe_allow_html=True)

# ─── Panel Data ────────────────────────────────────────────────────────────────
PANELS = [
    {
        "tier": "premium",
        "tier_label": "⭐ Premium",
        "name": "Maxeon 6 Series",
        "brand": "Maxeon Solar Technologies",
        "tagline": "Industry-leading efficiency and the only 40-year warranty on the market.",
        "wattage": 440,
        "efficiency": 22.8,
        "warranty": 40,
        "price_per_watt": 3.35,
        "dimensions": '68.9" × 41.2"',
        "cell_type": "IBC (Back Contact)",
        "degradation": "0.25%/yr",
        "temp_coeff": "-0.29°C",
        "best_for": "Limited roof space or clients who want the absolute best and plan to stay in their home long-term.",
        "image_url": "https://images.squarespace-cdn.com/content/v1/5e31f9e3e3b3d4326bf61498/1679521735600-VZ9HFJ3P7MKGXQUQZZ21/Maxeon+Solar+Panel.jpg",
    },
    {
        "tier": "premium",
        "tier_label": "⭐ Premium",
        "name": "Alpha Pure RX 470W",
        "brand": "REC Group",
        "tagline": "Best temperature performance in the industry — ideal for hot California roofs.",
        "wattage": 470,
        "efficiency": 22.6,
        "warranty": 25,
        "price_per_watt": 2.85,
        "dimensions": '70.1" × 41.4"',
        "cell_type": "HJT (Heterojunction)",
        "degradation": "0.25%/yr",
        "temp_coeff": "-0.26°C",
        "best_for": "Hot climates like Santa Cruz and Central Valley where summer heat affects output the most.",
        "image_url": "https://www.ecowatch.com/wp-content/uploads/2023/08/rec-alpha-pure.jpg",
    },
    {
        "tier": "value",
        "tier_label": "✅ Best Value",
        "name": "Q.TRON BLK-G2+ 430W",
        "brand": "Hanwha Qcells",
        "tagline": "Most popular residential panel in the U.S. — made in Georgia, proven reliability.",
        "wattage": 430,
        "efficiency": 21.5,
        "warranty": 25,
        "price_per_watt": 2.48,
        "dimensions": '69.3" × 41.2"',
        "cell_type": "N-Type Mono",
        "degradation": "0.40%/yr",
        "temp_coeff": "-0.30°C",
        "best_for": "Most residential clients — the best combination of price, quality, and U.S. manufacturing.",
        "image_url": "https://www.ecowatch.com/wp-content/uploads/2023/04/qcells-solar-panel.jpg",
    },
    {
        "tier": "value",
        "tier_label": "✅ Best Value",
        "name": "TOPHiKu6 460W",
        "brand": "Canadian Solar",
        "tagline": "Massive 460W output with TOPCon tech at a price that makes larger systems affordable.",
        "wattage": 460,
        "efficiency": 22.5,
        "warranty": 25,
        "price_per_watt": 2.55,
        "dimensions": '71.9" × 42.1"',
        "cell_type": "N-Type TOPCon",
        "degradation": "0.35%/yr",
        "temp_coeff": "-0.29°C",
        "best_for": "Clients who want high wattage and excellent efficiency without the premium price tag.",
        "image_url": "https://www.ecowatch.com/wp-content/uploads/2023/09/canadian-solar-panel.jpg",
    },
    {
        "tier": "budget",
        "tier_label": "💰 Budget-Friendly",
        "name": "Tiger Neo 420W",
        "brand": "Jinko Solar",
        "tagline": "One of the world's best-selling panels — reliable output at the lowest installed cost.",
        "wattage": 420,
        "efficiency": 21.6,
        "warranty": 25,
        "price_per_watt": 2.20,
        "dimensions": '68.7" × 41.1"',
        "cell_type": "N-Type TOPCon",
        "degradation": "0.40%/yr",
        "temp_coeff": "-0.30°C",
        "best_for": "Budget-conscious clients or large systems where keeping cost-per-watt low matters most.",
        "image_url": "https://www.ecowatch.com/wp-content/uploads/2023/08/jinko-solar-panel.jpg",
    },
]

TIER_ORDER = ["premium", "value", "budget"]
TIER_LABELS_MAP = {
    "premium": "Premium Panels",
    "value":   "Best Value Panels",
    "budget":  "Budget-Friendly Panels",
}

def render_card(p):
    tier_css = f"tier-{p['tier']}"
    st.markdown(f"""
    <div class="panel-card">
        <div class="panel-img-wrap">
            <img src="{p['image_url']}" alt="{p['name']}" onerror="this.style.display='none'"/>
        </div>
        <div class="panel-body">
            <div class="panel-tier {tier_css}">{p['tier_label']}</div>
            <div class="panel-name">{p['name']}</div>
            <div class="panel-tagline">{p['brand']} &nbsp;·&nbsp; {p['tagline']}</div>

            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-box-label">Output</div>
                    <div class="stat-box-val">{p['wattage']}</div>
                    <div class="stat-box-unit">watts</div>
                </div>
                <div class="stat-box">
                    <div class="stat-box-label">Efficiency</div>
                    <div class="stat-box-val">{p['efficiency']}</div>
                    <div class="stat-box-unit">%</div>
                </div>
                <div class="stat-box">
                    <div class="stat-box-label">Warranty</div>
                    <div class="stat-box-val">{p['warranty']}</div>
                    <div class="stat-box-unit">years</div>
                </div>
            </div>

            <div class="stat-box-wide">
                <span class="stat-box-wide-label">Price per watt</span>
                <span class="stat-box-wide-val">${p['price_per_watt']:.2f}/W</span>
            </div>
            <div class="stat-box-wide">
                <span class="stat-box-wide-label">Dimensions</span>
                <span class="stat-box-wide-val">{p['dimensions']}</span>
            </div>
            <div class="stat-box-wide">
                <span class="stat-box-wide-label">Cell type</span>
                <span class="stat-box-wide-val">{p['cell_type']}</span>
            </div>
            <div class="stat-box-wide">
                <span class="stat-box-wide-label">Annual degradation</span>
                <span class="stat-box-wide-val">{p['degradation']}</span>
            </div>
            <div class="stat-box-wide">
                <span class="stat-box-wide-label">Temp. coefficient</span>
                <span class="stat-box-wide-val">{p['temp_coeff']}</span>
            </div>

            <div class="best-for"><strong>Best for:</strong> {p['best_for']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── Page ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">🔆 Solar Panel Catalog</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Panels we recommend for residential installs — from premium to budget-friendly.</div>', unsafe_allow_html=True)

for tier in TIER_ORDER:
    tier_panels = [p for p in PANELS if p["tier"] == tier]
    if tier_panels:
        st.markdown(f'<div class="divider-label">{TIER_LABELS_MAP[tier]}</div>', unsafe_allow_html=True)
        for panel in tier_panels:
            render_card(panel)

st.caption("Pricing reflects 2025 U.S. installer cost per watt. Retail prices vary by region and supplier. All panels shown are monocrystalline N-type — the current industry standard for residential installations.")
