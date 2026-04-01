# Mohrfeld Solar — Tools

A growing set of tools for residential solar sales and estimation.

---

## Projects

### 1. Solar Rooftop Estimator (`app_v4.py`)
Enter any address to get an instant solar analysis — roof area, system size, cost estimate, savings projection, and 25-year payback chart.

**Powered by:**
- Google Solar API (roof analysis)
- OpenStreetMap / Overpass API (fallback footprint detection)
- State-level utility rates + NREL sun hour data (savings math)

**Run locally:**
```bash
pip3 install streamlit requests python-dotenv plotly
streamlit run app_v4.py
```

Add a `.env` file with your Google API key:
```
GOOGLE_API_KEY=your_key_here
```

---

### 2. Panel Catalog (`panels.html`)
A swipeable product catalog of recommended residential solar panels with real 2025 specs.

**Open directly in any browser — no install needed:**
```bash
open panels.html
```

Panels included: Maxeon 6, REC Alpha Pure RX, Qcells Q.Tron BLK-G2+, Canadian Solar TOPHiKu6, Jinko Tiger Neo.

---

## Setup

**Requirements for the Streamlit app:**
```
streamlit
requests
python-dotenv
plotly
```

Install all at once:
```bash
pip3 install streamlit requests python-dotenv plotly
```

---

## Roadmap

- [ ] ROI calculator with state incentives
- [ ] PVWatts API integration for energy production estimates  
- [ ] Lead capture landing page
- [ ] Website to host all tools

---

*Built for Mohrfeld Solar — Santa Cruz, CA*
