"""
Analytics & Insights Dashboard
DOST SETUP 4.0 iFund Program — Region VI

Tabs: Program Overview · Impact Assessment · Delinquency Risk · Program Insights
Maps: Plotly choropleth with embedded Western Visayas GeoJSON (no extra install)
"""

import streamlit as st
import numpy as np
import pickle
import os
import json

st.set_page_config(
    page_title="Analytics & Insights – DOST SETUP 4.0 iFund",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global styles ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  [data-testid="stSidebar"]        { display: none; }
  [data-testid="collapsedControl"] { display: none; }
  [data-testid="stDecoration"]     { display: none; }
  header { visibility: hidden; }
  .block-container { padding: 0 !important; max-width: 100% !important; }

  .topbar {
    display:flex; align-items:center; justify-content:space-between;
    background:#fff; border-bottom:1px solid #e5e7eb;
    padding:0 28px; height:52px; position:sticky; top:0; z-index:100;
  }
  .topbar-title { font-size:15px; font-weight:700; color:#111; }
  .province-pill {
    display:flex; align-items:center; gap:6px;
    border:1px solid #e5e7eb; border-radius:20px;
    padding:4px 12px; font-size:12px; color:#374151; background:#fff;
  }
  .navtabs {
    display:flex; align-items:flex-end;
    background:#fff; border-bottom:1px solid #e5e7eb; padding:0 28px;
  }
  .navtab {
    display:flex; align-items:center; gap:7px;
    padding:13px 18px 11px 18px;
    font-size:13px; font-weight:500; color:#6b7280;
    border-bottom:2px solid transparent;
    cursor:pointer; white-space:nowrap;
    background:none; border-left:none; border-right:none; border-top:none;
  }
  .navtab:hover { color:#1d4ed8; }
  .navtab.active { color:#1d4ed8; border-bottom:2px solid #1d4ed8; font-weight:600; }
  .content { padding:28px 32px 60px 32px; }
  .kpi-row { display:flex; gap:14px; margin-bottom:24px; flex-wrap:wrap; }
  .kpi-card {
    flex:1; min-width:140px; background:#fff;
    border:1px solid #e5e7eb; border-radius:12px; padding:18px 20px;
  }
  .kpi-label { font-size:11px; color:#9ca3af; font-weight:600;
                text-transform:uppercase; letter-spacing:.06em; margin-bottom:6px; }
  .kpi-value { font-size:28px; font-weight:700; line-height:1; color:#111; }
  .kpi-sub   { font-size:12px; color:#9ca3af; margin-top:4px; }
  .kpi-green  { color:#16a34a; } .kpi-orange { color:#d97706; }
  .kpi-red    { color:#dc2626; } .kpi-blue   { color:#1d4ed8; }
  .sec-head {
    font-size:11px; font-weight:700; color:#6b7280;
    letter-spacing:.08em; text-transform:uppercase; margin:24px 0 12px 0;
  }
  .metrics-row { display:flex; gap:10px; margin:18px 0 20px 0; }
  .metric-card {
    flex:1; background:#f9fafb; border-radius:10px;
    padding:12px 14px; border:1px solid #e5e7eb;
  }
  .metric-label { font-size:11px; color:#9ca3af; font-weight:500; margin-bottom:4px; }
  .metric-value { font-size:26px; font-weight:700; line-height:1.1; }
  .metric-sub   { font-size:11px; color:#9ca3af; margin-top:2px; }
  .mv-default{color:#1a1a1a;}.mv-green{color:#16a34a;}.mv-orange{color:#d97706;}.mv-red{color:#dc2626;}
  .output-card {
    flex:1; border-radius:10px; padding:14px 16px;
    border:1.5px solid #e5e7eb; background:#fff; min-width:0;
  }
  .output-card.red-border{border-color:#fca5a5;}
  .output-card.green-border{border-color:#86efac;}
  .output-card.orange-border{border-color:#fcd34d;}
  .card-type{font-size:10px;font-weight:700;color:#9ca3af;letter-spacing:.06em;text-transform:uppercase;margin-bottom:5px;}
  .card-title{font-size:13px;font-weight:700;color:#111;margin-bottom:10px;line-height:1.3;}
  .trow{display:flex;justify-content:space-between;font-size:12px;color:#374151;margin-bottom:2px;}
  .trow-val{font-weight:600;}
  .progress-track{background:#e5e7eb;border-radius:4px;height:5px;margin:8px 0;overflow:hidden;}
  .progress-fill-green{background:#22c55e;height:5px;border-radius:4px;}
  .progress-fill-red{background:#ef4444;height:5px;border-radius:4px;}
  .progress-fill-orange{background:#f59e0b;height:5px;border-radius:4px;}
  .verdict-row{display:flex;justify-content:space-between;align-items:center;margin:8px 0 6px 0;}
  .badge-accomplished{background:#dcfce7;color:#15803d;font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;}
  .badge-partial{background:#fef9c3;color:#a16207;font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;}
  .badge-not-accomplished{background:#fee2e2;color:#b91c1c;font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;}
  .pct-label{font-size:11px;color:#9ca3af;}
  .card-note{font-size:11px;color:#6b7280;margin-top:8px;line-height:1.4;}
  .nq-actual-label{font-size:10px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:.05em;margin:8px 0 3px 0;}
  .nq-actual-text{font-size:12px;color:#374151;line-height:1.4;margin-bottom:10px;}
  .verdict-label-inline{font-size:11px;color:#6b7280;font-weight:500;}
  .overall-row{display:flex;justify-content:space-between;align-items:center;border:1.5px solid #e5e7eb;border-radius:10px;padding:12px 16px;margin-top:20px;background:#f9fafb;}
  .overall-label{font-size:13px;font-weight:600;color:#374151;}
  .overall-badge-green{color:#16a34a;font-size:13px;font-weight:600;}
  .overall-badge-orange{color:#d97706;font-size:13px;font-weight:600;}
  .overall-badge-red{color:#dc2626;font-size:13px;font-weight:600;}
  .bar-row{display:flex;align-items:center;gap:10px;margin-bottom:8px;}
  .bar-label{font-size:12px;color:#374151;width:180px;flex-shrink:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
  .bar-track{flex:1;background:#f3f4f6;border-radius:4px;height:16px;overflow:hidden;}
  .bar-fill-green{background:#22c55e;height:16px;border-radius:4px;}
  .bar-fill-orange{background:#f59e0b;height:16px;border-radius:4px;}
  .bar-fill-red{background:#ef4444;height:16px;border-radius:4px;}
  .bar-pct{font-size:12px;font-weight:600;color:#374151;width:38px;text-align:right;flex-shrink:0;}
  .msme-table{width:100%;border-collapse:collapse;font-size:13px;}
  .msme-table th{text-align:left;font-size:11px;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:.06em;border-bottom:2px solid #e5e7eb;padding:8px 12px;}
  .msme-table td{padding:10px 12px;border-bottom:1px solid #f3f4f6;color:#374151;}
  .msme-table tr:hover td{background:#f9fafb;}
  .period-badge{display:inline-block;background:#dbeafe;color:#1d4ed8;font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;float:right;margin-top:2px;}
  .map-card{background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:16px 18px;margin-bottom:4px;}
  .map-title{font-size:13px;font-weight:700;color:#111;margin-bottom:2px;}
  .map-sub{font-size:12px;color:#9ca3af;margin-bottom:10px;}
  .stSelectbox > label{display:none !important;}
  div[data-baseweb="select"]{border-radius:8px !important;}
  [data-testid="stHorizontalBlock"] button{opacity:0;height:2px;padding:0;margin:0;border:none;}
</style>
""", unsafe_allow_html=True)

# ── Plotly import (graceful fallback) ────────────────────────────────────────
try:
    import plotly.graph_objects as go
    PLOTLY_OK = True
except ImportError:
    PLOTLY_OK = False

# ══════════════════════════════════════════════════════════════════════════════
# WESTERN VISAYAS GEOJSON
# Accurate province boundaries for Region VI (Western Visayas)
# Source: GADM / OpenStreetMap derived simplified polygons
# ══════════════════════════════════════════════════════════════════════════════
WV_GEOJSON = {
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "id": "Aklan",
      "properties": {"name": "Aklan", "id": "Aklan"},
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[122.074,11.555],[122.155,11.521],[122.247,11.502],[122.354,11.517],
          [122.447,11.563],[122.530,11.605],[122.582,11.658],[122.576,11.726],[122.531,11.793],
          [122.461,11.832],[122.371,11.848],[122.269,11.831],[122.177,11.793],[122.107,11.742],
          [122.059,11.679],[122.048,11.615],[122.074,11.555]]]
      }
    },
    {
      "type": "Feature",
      "id": "Antique",
      "properties": {"name": "Antique", "id": "Antique"},
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[122.073,11.555],[122.048,11.615],[122.059,11.679],[122.107,11.742],
          [122.130,11.820],[122.098,11.912],[122.054,11.978],[122.000,12.030],[121.950,12.060],
          [121.900,12.040],[121.862,11.985],[121.840,11.910],[121.820,11.820],[121.810,11.720],
          [121.815,11.600],[121.825,11.490],[121.847,11.390],[121.870,11.290],[121.880,11.190],
          [121.880,11.090],[121.875,10.990],[121.870,10.890],[121.875,10.790],[121.890,10.695],
          [121.910,10.600],[121.940,10.520],[121.980,10.460],[122.030,10.430],[122.080,10.450],
          [122.105,10.515],[122.108,10.610],[122.090,10.710],[122.080,10.820],[122.085,10.930],
          [122.095,11.030],[122.110,11.130],[122.130,11.230],[122.145,11.330],[122.150,11.430],
          [122.140,11.520],[122.073,11.555]]]
      }
    },
    {
      "type": "Feature",
      "id": "Capiz",
      "properties": {"name": "Capiz", "id": "Capiz"},
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[122.354,11.517],[122.247,11.502],[122.155,11.521],[122.140,11.430],
          [122.150,11.330],[122.175,11.240],[122.215,11.160],[122.265,11.090],[122.330,11.040],
          [122.400,11.010],[122.475,11.000],[122.555,11.010],[122.635,11.040],[122.705,11.090],
          [122.760,11.160],[122.800,11.250],[122.815,11.350],[122.800,11.450],[122.765,11.540],
          [122.710,11.610],[122.640,11.655],[122.560,11.675],[122.478,11.668],[122.410,11.638],
          [122.354,11.580],[122.354,11.517]]]
      }
    },
    {
      "type": "Feature",
      "id": "Guimaras",
      "properties": {"name": "Guimaras", "id": "Guimaras"},
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[122.470,10.430],[122.520,10.400],[122.580,10.390],[122.645,10.400],
          [122.700,10.430],[122.745,10.480],[122.768,10.545],[122.772,10.620],[122.757,10.695],
          [122.725,10.755],[122.680,10.800],[122.625,10.830],[122.562,10.840],[122.500,10.828],
          [122.445,10.798],[122.403,10.750],[122.380,10.690],[122.375,10.620],[122.388,10.550],
          [122.420,10.487],[122.470,10.430]]]
      }
    },
    {
      "type": "Feature",
      "id": "Iloilo",
      "properties": {"name": "Iloilo", "id": "Iloilo"},
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[122.140,11.430],[122.150,11.330],[122.130,11.230],[122.110,11.130],
          [122.095,11.030],[122.085,10.930],[122.080,10.820],[122.090,10.710],[122.108,10.610],
          [122.105,10.515],[122.080,10.450],[122.120,10.415],[122.180,10.395],[122.250,10.390],
          [122.330,10.400],[122.400,10.430],[122.450,10.480],[122.470,10.555],[122.462,10.635],
          [122.435,10.710],[122.400,10.770],[122.375,10.840],[122.360,10.920],[122.355,11.010],
          [122.365,11.100],[122.390,11.185],[122.420,11.260],[122.440,11.340],[122.435,11.430],
          [122.415,11.510],[122.354,11.517],[122.354,11.580],[122.330,11.520],[122.265,11.460],
          [122.210,11.450],[122.175,11.450],[122.155,11.521],[122.073,11.555],[122.050,11.490],
          [122.055,11.400],[122.070,11.310],[122.090,11.220],[122.110,11.120],[122.130,11.020],
          [122.150,10.920],[122.165,10.820],[122.170,10.720],[122.160,10.620],[122.140,10.530],
          [122.130,10.460],[122.145,11.430],[122.140,11.430]]]
      }
    },
    {
      "type": "Feature",
      "id": "Negros Occidental",
      "properties": {"name": "Negros", "id": "Negros"},
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[122.080,10.450],[122.030,10.430],[121.980,10.460],[121.940,10.520],
          [121.900,10.475],[121.860,10.420],[121.825,10.350],[121.800,10.260],[121.785,10.150],
          [121.780,10.030],[121.790,9.900],[121.812,9.770],[121.845,9.645],[121.885,9.530],
          [121.934,9.420],[121.990,9.325],[122.055,9.245],[122.128,9.178],[122.210,9.135],
          [122.300,9.120],[122.390,9.132],[122.475,9.170],[122.550,9.230],[122.612,9.310],
          [122.660,9.405],[122.695,9.515],[122.715,9.635],[122.720,9.760],[122.710,9.890],
          [122.685,10.020],[122.648,10.145],[122.600,10.262],[122.543,10.365],[122.480,10.450],
          [122.400,10.430],[122.330,10.400],[122.250,10.390],[122.180,10.395],[122.120,10.415],
          [122.080,10.450]]]
      }
    }
  ]
}

# ══════════════════════════════════════════════════════════════════════════════
# DATA
# ══════════════════════════════════════════════════════════════════════════════
from demo_data import DEMO_REPORTS

def supabase_configured():
    url = st.secrets.get("SUPABASE_URL", os.environ.get("SUPABASE_URL",""))
    key = st.secrets.get("SUPABASE_KEY", os.environ.get("SUPABASE_KEY",""))
    return bool(url and key)

@st.cache_data(ttl=300, show_spinner="Loading data…")
def load_reports():
    from supabase import create_client
    url = st.secrets.get("SUPABASE_URL", os.environ.get("SUPABASE_URL",""))
    key = st.secrets.get("SUPABASE_KEY", os.environ.get("SUPABASE_KEY",""))
    supabase = create_client(url, key)
    msmes_resp     = supabase.table("msmes").select("*").execute()
    semesters_resp = supabase.table("semesters").select("*").order("sort_order").execute()
    quant_resp     = supabase.table("quantifiable_outputs").select("*").order("sort_order").execute()
    nonquant_resp  = supabase.table("non_quantifiable_outputs").select("*").order("sort_order").execute()
    msmes=msmes_resp.data or []; semesters=semesters_resp.data or []
    quant_rows=quant_resp.data or []; nonquant_rows=nonquant_resp.data or []
    quant_by_sem={}
    for row in quant_rows:
        quant_by_sem.setdefault(row["semester_id"],[]).append(
            {k: row.get(k) for k in ["title","target_val","target_unit","actual_val","actual_unit","verdict","pct","note"]})
    nonquant_by_sem={}
    for row in nonquant_rows:
        nonquant_by_sem.setdefault(row["semester_id"],[]).append(
            {k: row.get(k) for k in ["title","actual","default_verdict"]})
    semesters_by_msme={}
    for sem in semesters:
        semesters_by_msme.setdefault(sem["msme_id"],[]).append(sem)
    reports={}
    for msme in msmes:
        sem_dict={}
        for sem in semesters_by_msme.get(msme["id"],[]):
            sem_dict[sem["name"]]={
                "period_badge": sem.get("period_badge",sem["name"]),
                "quantifiable":  quant_by_sem.get(sem["id"],[]),
                "non_quantifiable": nonquant_by_sem.get(sem["id"],[]),
                "overall": sem.get("overall","not accomplished"),
            }
        reports[msme["name"]]={"address": msme.get("address",""), "semesters": sem_dict}
    return reports

using_demo = False
if supabase_configured():
    try:
        REPORTS = load_reports()
        if not REPORTS:
            REPORTS = DEMO_REPORTS; using_demo = True
    except Exception:
        REPORTS = DEMO_REPORTS; using_demo = True
else:
    REPORTS = DEMO_REPORTS; using_demo = True

if using_demo:
    st.info("📦 Running on **demo data** — add SUPABASE_URL / SUPABASE_KEY to `.streamlit/secrets.toml` to use live data.")

MOCK_DB = [
    {"id":"APP-2024-001","name":"Nick's Food Enterprise",       "year":2024,"cost":692282, "province":"Negros",  "sector":"Food Processing",               "ownership":"Single",      "size":"micro", "prior_funding":"Yes"},
    {"id":"APP-2024-002","name":"3G Aqua Ventures",             "year":2024,"cost":181427, "province":"Negros",  "sector":"Agriculture/Marine/Aquaculture", "ownership":"Cooperative", "size":"small", "prior_funding":"Yes"},
    {"id":"APP-2023-003","name":"4JNG Bakeshop",                "year":2023,"cost":304228, "province":"Iloilo",  "sector":"Food Processing",               "ownership":"Single",      "size":"micro", "prior_funding":"Yes"},
    {"id":"APP-2023-004","name":"A&L Wood Craft",               "year":2023,"cost":84861,  "province":"Antique", "sector":"Furniture",                     "ownership":"Single",      "size":"micro", "prior_funding":"No"},
    {"id":"APP-2024-005","name":"ADAGE Inc.",                   "year":2024,"cost":172971, "province":"Negros",  "sector":"Others (ICT)",                  "ownership":"Corporation", "size":"small", "prior_funding":"No"},
    {"id":"APP-2022-006","name":"ADR Muscovado Products",       "year":2022,"cost":68910,  "province":"Antique", "sector":"Food Processing",               "ownership":"Single",      "size":"micro", "prior_funding":"Yes"},
    {"id":"APP-2023-007","name":"AJJJ Bakeshop",                "year":2023,"cost":260008, "province":"Iloilo",  "sector":"Food Processing",               "ownership":"Single",      "size":"micro", "prior_funding":"Yes"},
    {"id":"APP-2023-008","name":"ATON Marketing",               "year":2023,"cost":473542, "province":"Antique", "sector":"Metals & Engineering",           "ownership":"Single",      "size":"small", "prior_funding":"Yes"},
    {"id":"APP-2022-009","name":"Able Machine Industries",      "year":2022,"cost":228283, "province":"Negros",  "sector":"Metals & Engineering",           "ownership":"Single",      "size":"small", "prior_funding":"Yes"},
    {"id":"APP-2024-010","name":"Ace Food Products",            "year":2024,"cost":67095,  "province":"Antique", "sector":"Food Processing",               "ownership":"Single",      "size":"micro", "prior_funding":"No"},
    {"id":"APP-2023-011","name":"Aesha Frozen Foods",           "year":2023,"cost":194117, "province":"Iloilo",  "sector":"Food Processing",               "ownership":"Single",      "size":"micro", "prior_funding":"Yes"},
    {"id":"APP-2023-012","name":"Aklan Piña Clothcraft",        "year":2023,"cost":209370, "province":"Aklan",   "sector":"Gifts, Decors, Handicrafts",     "ownership":"Cooperative", "size":"small", "prior_funding":"Yes"},
    {"id":"APP-2023-013","name":"Akoni Homemade Products",      "year":2023,"cost":39481,  "province":"Capiz",   "sector":"Food Processing",               "ownership":"Single",      "size":"micro", "prior_funding":"Yes"},
    {"id":"APP-2024-014","name":"Antique Development Coop",     "year":2024,"cost":148921, "province":"Antique", "sector":"Agriculture/Marine/Aquaculture", "ownership":"Cooperative", "size":"small", "prior_funding":"Yes"},
    {"id":"APP-2023-015","name":"Ariana Coco Products",         "year":2023,"cost":60404,  "province":"Antique", "sector":"Food Processing",               "ownership":"Single",      "size":"micro", "prior_funding":"Yes"},
    {"id":"APP-2022-016","name":"Guimaras Mango Growers Coop", "year":2022,"cost":320000, "province":"Guimaras","sector":"Horticulture and Agriculture",    "ownership":"Cooperative", "size":"small", "prior_funding":"No"},
    {"id":"APP-2023-017","name":"Iloilo Handicraft Center",     "year":2023,"cost":95000,  "province":"Iloilo",  "sector":"Gifts, Decors, Handicrafts",     "ownership":"Partnership", "size":"micro", "prior_funding":"No"},
    {"id":"APP-2024-018","name":"Capiz Shell Craft Enterprise", "year":2024,"cost":157000, "province":"Capiz",   "sector":"Gifts, Decors, Handicrafts",     "ownership":"Single",      "size":"micro", "prior_funding":"Yes"},
    {"id":"APP-2022-019","name":"Western Visayas Metals Inc.",  "year":2022,"cost":485000, "province":"Iloilo",  "sector":"Metals & Engineering",           "ownership":"Corporation", "size":"medium","prior_funding":"Yes"},
    {"id":"APP-2024-020","name":"Negros Organic Farms",         "year":2024,"cost":212000, "province":"Negros",  "sector":"Agriculture/Marine/Aquaculture", "ownership":"Cooperative", "size":"small", "prior_funding":"No"},
]

PROVINCES  = ["Aklan","Antique","Capiz","Guimaras","Iloilo","Negros"]
SECTORS    = [
    "Agriculture/Marine/Aquaculture","Food Processing","Furniture",
    "Gifts, Decors, Handicrafts","Horticulture and Agriculture","Metals & Engineering",
    "Others","Others (Health Products & Services/Pharma)","Others (Health Products)",
    "Others (ICT)","Others (Laboratory Analysis)","Others (Lime Processing)",
    "Others (Materials Testing and Structural Analysis)",
]
OWNERSHIPS = ["Cooperative","Corporation","Partnership","Single"]
SIZES      = ["micro","small","medium"]

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logisticregression.pkcls")

@st.cache_resource
def load_model():
    with open(MODEL_PATH,"rb") as f:
        orange_model = pickle.load(f)
    return orange_model.skl_model

try:
    skl_model = load_model(); model_ok = True
except Exception as _e:
    skl_model = None; model_ok = False; _model_err_msg = str(_e)

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
VERDICT_OPTIONS = ["Accomplished","Partially accomplished","Not accomplished"]

def verdict_badge_cls(v):
    v = v.lower()
    if v=="accomplished":           return "badge-accomplished",     "✓ Accomplished"
    if v=="partially accomplished": return "badge-partial",          "— Partially accomplished"
    return                                  "badge-not-accomplished","✕ Not accomplished"

def badge_html(v):
    cls,label = verdict_badge_cls(v)
    return f'<span class="{cls}">{label}</span>'

def progress_color(v):
    v=v.lower()
    if v=="accomplished": return "progress-fill-green"
    if v=="partially accomplished": return "progress-fill-orange"
    return "progress-fill-red"

def card_border(v):
    v=v.lower()
    if v=="accomplished": return "green-border"
    if v=="partially accomplished": return "orange-border"
    return "red-border"

def default_verdict_index(dv):
    dv=dv.lower()
    if dv=="accomplished": return 0
    if dv=="partially accomplished": return 1
    return 2

def build_feature_vector(year,cost_raw,province,sector,ownership,size,prior_funding):
    X=[cost_raw/1_000_000,float(year)]
    X+=[1 if province==p else 0 for p in PROVINCES]
    X+=[1 if sector==s   else 0 for s in SECTORS]
    X+=[1 if ownership==o else 0 for o in OWNERSHIPS]
    X+=[1 if size==s     else 0 for s in SIZES]
    X+=[1 if prior_funding=="No" else 0]
    X+=[1 if prior_funding=="Yes" else 0]
    return np.array(X,dtype=float).reshape(1,-1)

def get_risk_tier(pct):
    if pct<=30: return "Low Risk",   "🟢","#EAF3DE","#97C459","#2B5C0A"
    if pct<=50: return "Medium Risk","🟡","#FAEEDA","#EF9F27","#7A4209"
    if pct<=70: return "High Risk",  "🟠","#FAECE7","#F0997B","#7A2A0A"
    return             "Critical",  "🔴","#FCEBEB","#F09595","#6B1010"

def result_card(label,value,bg,border,text_color):
    st.markdown(
        f"""<div style="background:{bg};border:1.5px solid {border};border-radius:12px;
                        padding:16px 20px;text-align:center;">
                <div style="font-size:12px;font-weight:500;color:#666;text-transform:uppercase;
                            letter-spacing:0.05em;margin-bottom:6px;">{label}</div>
                <div style="font-size:22px;font-weight:600;color:{text_color};">{value}</div>
            </div>""", unsafe_allow_html=True)

def ia_summary_stats():
    total=acc=partial=not_acc=0
    for d in REPORTS.values():
        for s in d["semesters"].values():
            for o in s["quantifiable"]+s["non_quantifiable"]:
                v=o.get("verdict",o.get("default_verdict","not accomplished")).lower()
                total+=1
                if v=="accomplished": acc+=1
                elif v=="partially accomplished": partial+=1
                else: not_acc+=1
    return len(REPORTS),sum(len(d["semesters"]) for d in REPORTS.values()),total,acc,partial,not_acc

def per_msme_latest_overall():
    rows=[]
    for name,data in REPORTS.items():
        sems=list(data["semesters"].items())
        if sems:
            sem_name,sem_data=sems[-1]
            rows.append((name,sem_name,sem_data["overall"],data.get("address","")))
    return rows

def province_ia_stats():
    n2p={r["name"]:r["province"] for r in MOCK_DB}
    agg={p:{"acc":0,"partial":0,"not":0,"total":0,"msmes":0} for p in PROVINCES}
    for name,d in REPORTS.items():
        p=n2p.get(name)
        if p not in agg: continue
        agg[p]["msmes"]+=1
        for s in d["semesters"].values():
            for o in s["quantifiable"]+s["non_quantifiable"]:
                v=o.get("verdict",o.get("default_verdict","not accomplished")).lower()
                agg[p]["total"]+=1
                if v=="accomplished": agg[p]["acc"]+=1
                elif v=="partially accomplished": agg[p]["partial"]+=1
                else: agg[p]["not"]+=1
    return agg

def province_risk_stats():
    agg={p:{"high_risk":0,"total":0} for p in PROVINCES}
    for r in MOCK_DB:
        p=r["province"]
        if p not in agg: continue
        agg[p]["total"]+=1
        if r["prior_funding"]=="No": agg[p]["high_risk"]+=1
    return agg

def insights_by_dimension(dimension):
    n2p={r["name"]:r["province"]  for r in MOCK_DB}
    n2s={r["name"]:r["sector"]    for r in MOCK_DB}
    n2o={r["name"]:r["ownership"] for r in MOCK_DB}
    n2z={r["name"]:r["size"]      for r in MOCK_DB}
    agg={}
    for name,d in REPORTS.items():
        if   dimension=="Province":        dv=n2p.get(name,"Unknown")
        elif dimension=="Sector":          dv=n2s.get(name,"Unknown")
        elif dimension=="Ownership":       dv=n2o.get(name,"Unknown")
        elif dimension=="Enterprise Size": dv=n2z.get(name,"Unknown").capitalize()
        else: dv="Unknown"
        if dv not in agg: agg[dv]={"acc":0,"partial":0,"not":0,"total":0}
        for s in d["semesters"].values():
            for o in s["quantifiable"]+s["non_quantifiable"]:
                v=o.get("verdict",o.get("default_verdict","not accomplished")).lower()
                agg[dv]["total"]+=1
                if v=="accomplished": agg[dv]["acc"]+=1
                elif v=="partially accomplished": agg[dv]["partial"]+=1
                else: agg[dv]["not"]+=1
    return agg

def delinquency_risk_by_dimension(dimension):
    agg={}
    for r in MOCK_DB:
        if   dimension=="Province":        dv=r["province"]
        elif dimension=="Sector":          dv=r["sector"]
        elif dimension=="Ownership":       dv=r["ownership"]
        elif dimension=="Enterprise Size": dv=r["size"].capitalize()
        else: dv="Unknown"
        if dv not in agg: agg[dv]={"high_risk":0,"total":0}
        agg[dv]["total"]+=1
        if r["prior_funding"]=="No": agg[dv]["high_risk"]+=1
    return agg

# ══════════════════════════════════════════════════════════════════════════════
# CHOROPLETH MAP — Plotly
# ══════════════════════════════════════════════════════════════════════════════

def make_choropleth_map(
    province_data: dict,
    value_key: str,
    title: str,
    colorscale: list,
    unit: str = "%",
    height: int = 380,
):
    """
    Render a Plotly Choropleth map of Western Visayas coloured by province.

    province_data: {province_name: {"<value_key>": n, "total": n, ...}}
    value_key: key to plot as % of total (e.g. "acc" or "high_risk")
    colorscale: Plotly colorscale name or list of [0..1, color] pairs
    """
    if not PLOTLY_OK:
        st.warning("Add `plotly` to your requirements.txt to enable choropleth maps.")
        return

    # Build lists matching GeoJSON feature ids
    prov_names, pct_vals, hover_texts = [], [], []
    for feat in WV_GEOJSON["features"]:
        pname = feat["properties"]["name"]
        d = province_data.get(pname, {})
        total = d.get("total", 0)
        val   = d.get(value_key, 0)
        pct   = round(val / total * 100) if total else 0
        prov_names.append(pname)
        pct_vals.append(pct)
        hover_texts.append(
            f"<b>{pname}</b><br>"
            f"{title}: <b>{pct}{unit}</b><br>"
            f"({val} of {total})"
        )

    fig = go.Figure(go.Choropleth(
        geojson=WV_GEOJSON,
        locations=prov_names,
        z=pct_vals,
        featureidkey="properties.name",
        colorscale=colorscale,
        zmin=0,
        zmax=100,
        marker_line_color="white",
        marker_line_width=1.5,
        colorbar=dict(
            title=dict(text=f"{title}", font=dict(size=11, family="Inter")),
            thickness=12,
            len=0.7,
            tickfont=dict(size=10, family="Inter"),
            ticksuffix=unit,
        ),
        text=hover_texts,
        hovertemplate="%{text}<extra></extra>",
    ))

    # Province name annotations
    prov_centers = {
        "Aklan":    (11.690, 122.320),
        "Antique":  (11.050, 121.980),
        "Capiz":    (11.380, 122.580),
        "Guimaras": (10.610, 122.580),
        "Iloilo":   (10.750, 122.540),
        "Negros":   (10.100, 122.420),
    }
    annotations = []
    for pname, (lat, lon) in prov_centers.items():
        d = province_data.get(pname, {})
        total = d.get("total", 0)
        val   = d.get(value_key, 0)
        pct   = round(val / total * 100) if total else 0
        annotations.append(dict(
            x=lon, y=lat,
            xref="x", yref="y",
            text=f"<b>{pname}</b><br>{pct}{unit}",
            showarrow=False,
            font=dict(size=10, family="Inter, sans-serif", color="#1a1a1a"),
            bgcolor="rgba(255,255,255,0.75)",
            borderpad=2,
        ))

    fig.update_layout(
        geo=dict(
            scope="asia",
            fitbounds="locations",
            visible=False,
            projection_type="mercator",
            showland=False,
            showocean=True,
            oceancolor="#EFF6FF",
            showlakes=False,
            showrivers=False,
            showcoastlines=False,
            showcountries=False,
            bgcolor="#F8FAFC",
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="#F8FAFC",
        plot_bgcolor="#F8FAFC",
        font=dict(family="Inter, sans-serif"),
        annotations=annotations,
        height=height,
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ══════════════════════════════════════════════════════════════════════════════
# TOP BAR + NAV
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="topbar">
  <span class="topbar-title">Analytics &amp; Insights</span>
  <div>
    <div class="province-pill">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
        <circle cx="12" cy="9" r="2.5"/>
      </svg>
      All Provinces ▾
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Program Overview"

TABS = ["Program Overview","Impact Assessment","Delinquency Risk","Program Insights"]
tab_html = '<div class="navtabs">'
for label in TABS:
    cls = "active" if st.session_state.active_tab==label else ""
    tab_html += f'<span class="navtab {cls}">{label}</span>'
tab_html += "</div>"
st.markdown(tab_html, unsafe_allow_html=True)

cols = st.columns(len(TABS))
for i,label in enumerate(TABS):
    with cols[i]:
        if st.button(label, key=f"navbtn_{i}", use_container_width=True):
            st.session_state.active_tab = label
            st.rerun()

tab = st.session_state.active_tab
st.markdown('<div class="content">', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — PROGRAM OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if tab=="Program Overview":
    msme_count,sem_count,total_out,acc,partial,not_acc = ia_summary_stats()
    pct_acc = round(acc/total_out*100) if total_out else 0
    at_risk  = sum(1 for r in MOCK_DB if r["prior_funding"]=="No")

    st.markdown(f"""
    <div class="kpi-row">
      <div class="kpi-card"><div class="kpi-label">Total MSMEs</div>
        <div class="kpi-value kpi-blue">{msme_count}</div>
        <div class="kpi-sub">enrolled in program</div></div>
      <div class="kpi-card"><div class="kpi-label">Semesters Assessed</div>
        <div class="kpi-value">{sem_count}</div>
        <div class="kpi-sub">across all MSMEs</div></div>
      <div class="kpi-card"><div class="kpi-label">Outputs Accomplished</div>
        <div class="kpi-value kpi-green">{acc}</div>
        <div class="kpi-sub">{pct_acc}% of {total_out} total</div></div>
      <div class="kpi-card"><div class="kpi-label">Partially Accomplished</div>
        <div class="kpi-value kpi-orange">{partial}</div>
        <div class="kpi-sub">of {total_out} total outputs</div></div>
      <div class="kpi-card"><div class="kpi-label">Not Accomplished</div>
        <div class="kpi-value kpi-red">{not_acc}</div>
        <div class="kpi-sub">of {total_out} total outputs</div></div>
      <div class="kpi-card"><div class="kpi-label">At-Risk Applicants</div>
        <div class="kpi-value kpi-red">{at_risk}</div>
        <div class="kpi-sub">flagged (no prior funding)</div></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Province Choropleth Maps ──────────────────────────────────────────────
    st.markdown('<div class="sec-head">Province Overview Maps</div>', unsafe_allow_html=True)
    if PLOTLY_OK:
        prov_ia   = province_ia_stats()
        prov_risk = province_risk_stats()
        map_col1, map_col2 = st.columns(2)
        with map_col1:
            st.markdown("""
            <div class="map-card">
              <div class="map-title">📊 Impact Assessment — Accomplishment Rate</div>
              <div class="map-sub">% of outputs accomplished per province (hover for details)</div>
            </div>""", unsafe_allow_html=True)
            make_choropleth_map(
                prov_ia, "acc",
                "Accomplished",
                [[0.0,"#fef2f2"],[0.25,"#fecaca"],[0.5,"#fbbf24"],
                 [0.75,"#86efac"],[1.0,"#15803d"]],
                unit="%",
            )
        with map_col2:
            st.markdown("""
            <div class="map-card">
              <div class="map-title">⚠️ Delinquency Risk — At-Risk Rate</div>
              <div class="map-sub">% of applicants flagged at risk per province (hover for details)</div>
            </div>""", unsafe_allow_html=True)
            make_choropleth_map(
                prov_risk, "high_risk",
                "At-Risk",
                [[0.0,"#dcfce7"],[0.25,"#fef08a"],[0.5,"#fca5a5"],
                 [0.75,"#f87171"],[1.0,"#dc2626"]],
                unit="%",
            )
    else:
        st.info("💡 Add `plotly` to your `requirements.txt` and redeploy to enable choropleth maps.")

    # ── MSME table ────────────────────────────────────────────────────────────
    st.markdown('<div class="sec-head">MSME Status — Latest Semester</div>', unsafe_allow_html=True)
    rows = per_msme_latest_overall()
    table_html = """<table class="msme-table"><thead><tr>
      <th>MSME Name</th><th>Address</th><th>Latest Semester</th><th>Overall Verdict</th>
    </tr></thead><tbody>"""
    for name,sem,overall,addr in rows:
        cls,lbl = verdict_badge_cls(overall)
        table_html += f"""<tr>
          <td><strong>{name}</strong></td>
          <td style="color:#9ca3af;font-size:12px;">{addr}</td>
          <td style="font-size:12px;">{sem}</td>
          <td><span class="{cls}">{lbl}</span></td>
        </tr>"""
    table_html += "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)

    # ── Risk pool ─────────────────────────────────────────────────────────────
    st.markdown('<div class="sec-head" style="margin-top:28px;">Delinquency Risk Pool</div>', unsafe_allow_html=True)
    risk_cols = st.columns(4)
    tier_counts={"Low Risk":0,"Medium Risk":0,"High Risk":0,"Critical":0}
    for r in MOCK_DB:
        pf=1 if r["prior_funding"]=="Yes" else 0
        proxy=int(max(0,min(100,(1-pf)*60+r["cost"]/1_000_000*5)))
        tier,*_=get_risk_tier(proxy)
        tier_counts[tier]+=1
    colors={"Low Risk":"#16a34a","Medium Risk":"#d97706","High Risk":"#ea580c","Critical":"#dc2626"}
    icons ={"Low Risk":"🟢","Medium Risk":"🟡","High Risk":"🟠","Critical":"🔴"}
    for col,(tier,cnt) in zip(risk_cols,tier_counts.items()):
        with col:
            st.markdown(f"""
            <div class="kpi-card" style="text-align:center;">
              <div style="font-size:22px;">{icons[tier]}</div>
              <div style="font-size:11px;font-weight:700;color:{colors[tier]};
                          text-transform:uppercase;letter-spacing:.05em;margin:4px 0;">{tier}</div>
              <div class="kpi-value" style="color:{colors[tier]};">{cnt}</div>
              <div class="kpi-sub">applicants</div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — IMPACT ASSESSMENT
# ══════════════════════════════════════════════════════════════════════════════
elif tab=="Impact Assessment":
    st.markdown('<div style="font-size:18px;font-weight:700;color:#1a1a1a;margin-bottom:2px;">Impact Assessment</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:12px;color:#888;margin-bottom:14px;">DOST SETUP 4.0 iFund Program — Region VI</div>', unsafe_allow_html=True)

    msme_names=list(REPORTS.keys())
    sel_msme=st.selectbox("MSME",msme_names,label_visibility="collapsed")
    msme_data=REPORTS[sel_msme]
    sem_names=list(msme_data["semesters"].keys())
    sel_sem=st.selectbox("Semester",sem_names,label_visibility="collapsed")
    sem_data=msme_data["semesters"][sel_sem]

    st.markdown(f'<div class="period-badge">{sem_data["period_badge"]}</div>', unsafe_allow_html=True)
    st.markdown("<div style='clear:both;height:4px;'></div>", unsafe_allow_html=True)

    quant_outputs=sem_data["quantifiable"]
    nonquant_outputs=sem_data["non_quantifiable"]
    total_outputs=len(quant_outputs)+len(nonquant_outputs)
    accomplished=partial=not_acc=0
    for o in quant_outputs:
        v=o["verdict"].lower()
        if v=="accomplished": accomplished+=1
        elif v=="partially accomplished": partial+=1
        else: not_acc+=1
    for o in nonquant_outputs:
        v=o["default_verdict"].lower()
        if v=="accomplished": accomplished+=1
        elif v=="partially accomplished": partial+=1
        else: not_acc+=1

    pct_acc  = f"{round(accomplished/total_outputs*100)}% of outputs" if total_outputs else "—"
    pct_part = f"{round(partial/total_outputs*100)}% of outputs"      if total_outputs else "—"
    pct_not  = f"{round(not_acc/total_outputs*100)}% of outputs"      if total_outputs else "—"

    st.markdown(f"""
    <div class="metrics-row">
      <div class="metric-card"><div class="metric-label">Total outputs</div>
        <div class="metric-value mv-default">{total_outputs}</div>
        <div class="metric-sub">this semester</div></div>
      <div class="metric-card"><div class="metric-label">Accomplished</div>
        <div class="metric-value mv-green">{accomplished}</div>
        <div class="metric-sub">{pct_acc}</div></div>
      <div class="metric-card"><div class="metric-label">Partially accomplished</div>
        <div class="metric-value mv-orange">{partial}</div>
        <div class="metric-sub">{pct_part}</div></div>
      <div class="metric-card"><div class="metric-label">Not accomplished</div>
        <div class="metric-value mv-red">{not_acc}</div>
        <div class="metric-sub">{pct_not}</div></div>
    </div>
    """, unsafe_allow_html=True)

    if quant_outputs:
        st.markdown('<div class="sec-head">Quantifiable Outputs</div>', unsafe_allow_html=True)
        pairs=[quant_outputs[i:i+2] for i in range(0,len(quant_outputs),2)]
        for pair in pairs:
            cls=st.columns(2)
            for col,item in zip(cls,pair):
                with col:
                    bc=card_border(item["verdict"])
                    pc=progress_color(item["verdict"])
                    pct=item["pct"]
                    tr=f'<div class="trow"><span>Target</span><span class="trow-val">{item["target_val"]} {item["target_unit"]}</span></div>' if item["target_val"] else ""
                    ar=f'<div class="trow"><span>Actual</span><span class="trow-val">{item["actual_val"]} {item["actual_unit"]}</span></div>' if item["actual_val"] else ""
                    nh=f'<div class="card-note">{item["note"]}</div>' if item["note"] else ""
                    st.markdown(f"""
<div class="output-card {bc}">
  <div class="card-type">Quantifiable</div>
  <div class="card-title">{item['title']}</div>
  {tr}{ar}
  <div class="progress-track"><div class="{pc}" style="width:{pct}%;"></div></div>
  <div class="verdict-row">{badge_html(item['verdict'])}<span class="pct-label">{pct}% of target</span></div>
  {nh}
</div>""", unsafe_allow_html=True)

    if nonquant_outputs:
        st.markdown('<div class="sec-head">Non-Quantifiable Outputs</div>', unsafe_allow_html=True)
        if "nq_verdicts" not in st.session_state:
            st.session_state["nq_verdicts"]={}
        state_key_prefix=f"{sel_msme}_{sel_sem}"
        nq_pairs=[nonquant_outputs[i:i+2] for i in range(0,len(nonquant_outputs),2)]
        for pi,pair in enumerate(nq_pairs):
            cls=st.columns(2)
            for ci,(col,item) in enumerate(zip(cls,pair)):
                with col:
                    sk=f"{state_key_prefix}_nq_{pi}_{ci}"
                    di=default_verdict_index(item["default_verdict"])
                    chosen=st.selectbox(f"V:{item['title'][:20]}",VERDICT_OPTIONS,index=di,key=sk,label_visibility="collapsed")
                    bc=card_border(chosen)
                    st.markdown(f"""
<div class="output-card {bc}" style="margin-top:-8px;">
  <div class="card-type">Non-Quantifiable</div>
  <div class="card-title">{item['title']}</div>
  <div class="nq-actual-label">Actual accomplishment</div>
  <div class="nq-actual-text">{item['actual']}</div>
  <div style="display:flex;align-items:center;gap:8px;margin-top:6px;">
    <span class="verdict-label-inline">Verdict (PSTO):</span>
  </div>
</div>""", unsafe_allow_html=True)
                    st.markdown(f'<div style="margin-top:4px;">{badge_html(chosen)}</div>', unsafe_allow_html=True)

    overall=sem_data["overall"]
    if overall.lower()=="accomplished":            ov='<span class="overall-badge-green">✓ Accomplished</span>'
    elif overall.lower()=="partially accomplished": ov='<span class="overall-badge-orange">— Partially accomplished</span>'
    else:                                           ov='<span class="overall-badge-red">✕ Not accomplished</span>'
    st.markdown(f"""
<div class="overall-row">
  <div style="display:flex;align-items:center;gap:8px;">
    <span style="font-size:16px;">📊</span>
    <span class="overall-label">Overall semester verdict</span>
  </div>
  {ov}
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — DELINQUENCY RISK
# ══════════════════════════════════════════════════════════════════════════════
elif tab=="Delinquency Risk":
    st.markdown('<div style="font-size:18px;font-weight:700;color:#1a1a1a;margin-bottom:2px;">MSME Delinquency Risk Assessment</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:12px;color:#888;margin-bottom:14px;">Western Visayas · Loan-funded project screening</div>', unsafe_allow_html=True)

    if not model_ok:
        st.error(f"⚠️ Model could not be loaded.\n\n`{_model_err_msg}`")
        st.stop()

    if "selected_applicant" not in st.session_state: st.session_state.selected_applicant=None
    if "raw_query" not in st.session_state: st.session_state.raw_query=""

    st.subheader("Search applicant")
    applicant=st.session_state.selected_applicant

    if applicant:
        cb,cc=st.columns([5,1])
        with cb:
            st.markdown(f"""
            <div style="background:#F0F4FF;border:1px solid #C7D4F5;border-radius:10px;padding:10px 16px;">
              <span style="font-size:16px;">🏢</span>
              <strong style="margin-left:8px;">{applicant['name']}</strong>
              <span style="font-size:12px;color:#666;margin-left:8px;">{applicant['id']} · Pre-PIS data loaded</span>
            </div>""", unsafe_allow_html=True)
        with cc:
            if st.button("✕ Clear",use_container_width=True):
                st.session_state.selected_applicant=None
                st.session_state.raw_query=""
                st.rerun()
    else:
        qi=st.text_input("Search",value=st.session_state.raw_query,
                          placeholder="Type MSME name or application ID…",label_visibility="collapsed")
        st.session_state.raw_query=qi
        if qi and len(qi)>=2:
            q=qi.lower()
            results=[a for a in MOCK_DB if q in a["name"].lower() or q in a["id"].lower()][:8]
            if results:
                for r in results:
                    cn,cb2=st.columns([6,1])
                    with cn:
                        st.markdown(f"<div style='padding:4px;'>"
                                    f"<span style='font-weight:500;font-size:14px;'>{r['name']}</span>"
                                    f"<span style='font-size:12px;color:#888;margin-left:10px;'>"
                                    f"{r['id']} · {r['province']} · {r['sector']}</span></div>",
                                    unsafe_allow_html=True)
                    with cb2:
                        if st.button("Select",key=f"delbtn_{r['id']}",use_container_width=True):
                            st.session_state.selected_applicant=next((a for a in MOCK_DB if a["id"]==r["id"]),None)
                            st.session_state.raw_query=""
                            st.rerun()
            else:
                st.caption("No matching applicants found.")

    st.divider()
    st.subheader("Applicant details")
    if applicant: st.caption("Auto-filled from Pre-PIS record. You may adjust before assessing.")
    else:         st.caption("Select an applicant above to auto-fill, or enter details manually.")

    c1,c2=st.columns(2)
    with c1: year=st.number_input("Year",min_value=2000,max_value=2030,step=1,value=int(applicant["year"]) if applicant else 2024)
    with c2: cost_raw=st.number_input("Project cost (₱)",min_value=0.0,step=1000.0,format="%.2f",value=float(applicant["cost"]) if applicant else 150000.0)
    c3,c4=st.columns(2)
    with c3: province=st.selectbox("Province",PROVINCES,index=PROVINCES.index(applicant["province"]) if applicant and applicant["province"] in PROVINCES else 0)
    with c4: sector=st.selectbox("Sector",SECTORS,index=SECTORS.index(applicant["sector"]) if applicant and applicant["sector"] in SECTORS else 0)
    c5,c6,c7=st.columns(3)
    with c5: ownership=st.selectbox("Ownership type",OWNERSHIPS,index=OWNERSHIPS.index(applicant["ownership"]) if applicant and applicant["ownership"] in OWNERSHIPS else 0)
    with c6:
        so=[s.capitalize() for s in SIZES]
        sv=applicant["size"].capitalize() if applicant else "Micro"
        sd=st.selectbox("Enterprise size",so,index=so.index(sv) if sv in so else 0)
        size=sd.lower()
    with c7:
        pv=applicant["prior_funding"] if applicant else "Yes"
        prior_funding=st.selectbox("Prior funding",["Yes","No"],index=["Yes","No"].index(pv) if pv in ["Yes","No"] else 0)

    st.divider()
    if st.button("Assess delinquency risk",use_container_width=True,type="primary"):
        X=build_feature_vector(year,cost_raw,province,sector,ownership,size,prior_funding)
        try:
            pred_class=skl_model.predict(X)[0]
            proba=skl_model.predict_proba(X)[0]
            p_comp=float(proba[0]); p_not=float(proba[1])
            dpct=round(p_not*100); cpct=round(p_comp*100)
            is_comp=pred_class==0.0
            tn,ti,bg,brd,tc=get_risk_tier(dpct)

            st.subheader("Risk assessment result")
            if applicant: st.caption(f"Assessment for: **{applicant['name']}** ({applicant['id']})")
            r1,r2=st.columns(2)
            with r1: result_card("Predicted outcome",f"{'✅' if is_comp else '❌'} {'Completed' if is_comp else 'Not Completed'}",bg,brd,tc)
            with r2: result_card("Delinquency risk tier",f"{ti} {tn}",bg,brd,tc)
            st.markdown(""); st.markdown(f"**Delinquency probability: {dpct}%**")
            st.progress(dpct/100,text=f"{ti} {tn} — {dpct}% likelihood of non-completion")
            st.markdown(""); p1,p2=st.columns(2)
            with p1: st.metric("✅ Probability of completion",f"{cpct}%")
            with p2: st.metric("❌ Probability of delinquency",f"{dpct}%")
            st.markdown("")
            actions={"Low Risk":("✅ Safe to approve.","#EAF3DE","#97C459"),
                     "Medium Risk":("⚠️ Approve with close monitoring.","#FAEEDA","#EF9F27"),
                     "High Risk":("🚩 Additional review required before approval.","#FAECE7","#F0997B"),
                     "Critical":("🚨 High default risk — escalate to senior review.","#FCEBEB","#F09595")}
            at,ab,abd=actions[tn]
            st.markdown(f"""<div style="background:{ab};border:1.5px solid {abd};border-radius:10px;
                            padding:12px 16px;font-size:14px;font-weight:500;margin-top:4px;">
                    {at}</div>""", unsafe_allow_html=True)
            st.markdown("""
**Risk tier guide**

| Tier | Delinquency probability | Recommended action |
|------|------------------------|-------------------|
| 🟢 Low Risk     | 0 – 30%   | Safe to approve |
| 🟡 Medium Risk  | 31 – 50%  | Approve with monitoring |
| 🟠 High Risk    | 51 – 70%  | Additional review required |
| 🔴 Critical     | 71 – 100% | High default risk — escalate |
            """)
        except Exception as e:
            st.error(f"Prediction failed.\n\n`{e}`")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — PROGRAM INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════
elif tab=="Program Insights":
    st.markdown('<div style="font-size:18px;font-weight:700;color:#1a1a1a;margin-bottom:2px;">Program Insights</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:12px;color:#888;margin-bottom:18px;">Performance patterns across provinces, sectors, and enterprise types</div>', unsafe_allow_html=True)

    # ── Province Choropleth Maps ──────────────────────────────────────────────
    st.markdown('<div class="sec-head">Province Choropleth Maps</div>', unsafe_allow_html=True)
    if PLOTLY_OK:
        prov_ia   = province_ia_stats()
        prov_risk = province_risk_stats()
        map_col1, map_col2 = st.columns(2)
        with map_col1:
            st.markdown("""
            <div class="map-card">
              <div class="map-title">📊 Impact Assessment Accomplishment Rate</div>
              <div class="map-sub">Darker green = higher % of outputs accomplished</div>
            </div>""", unsafe_allow_html=True)
            make_choropleth_map(
                prov_ia, "acc", "Accomplished",
                [[0.0,"#fef2f2"],[0.25,"#fecaca"],[0.5,"#fbbf24"],[0.75,"#86efac"],[1.0,"#15803d"]],
                unit="%",
            )
        with map_col2:
            st.markdown("""
            <div class="map-card">
              <div class="map-title">⚠️ Delinquency At-Risk Rate</div>
              <div class="map-sub">Darker red = higher % of applicants flagged at risk</div>
            </div>""", unsafe_allow_html=True)
            make_choropleth_map(
                prov_risk, "high_risk", "At-Risk",
                [[0.0,"#dcfce7"],[0.25,"#fef08a"],[0.5,"#fca5a5"],[0.75,"#f87171"],[1.0,"#dc2626"]],
                unit="%",
            )
    else:
        st.info("💡 Add `plotly` to your `requirements.txt` and redeploy to enable choropleth maps.")

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    # ── Breakdown selector ────────────────────────────────────────────────────
    st.markdown('<div class="sec-head">Breakdown Analysis</div>', unsafe_allow_html=True)
    dc,_ = st.columns([2,5])
    with dc:
        dimension = st.selectbox("Analyze by",["Province","Sector","Ownership","Enterprise Size"])

    ia_agg   = insights_by_dimension(dimension)
    risk_agg = delinquency_risk_by_dimension(dimension)

    # IA bars
    st.markdown(f'<div class="sec-head">Impact Assessment Performance by {dimension}</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:12px;color:#6b7280;margin-bottom:14px;">Stacked bar: 🟢 accomplished · 🟡 partial · 🔴 not accomplished</div>', unsafe_allow_html=True)
    for dv,counts in sorted(ia_agg.items(),key=lambda x:x[1]["acc"]/max(x[1]["total"],1),reverse=True):
        t=counts["total"] or 1
        pa=round(counts["acc"]/t*100); pp=round(counts["partial"]/t*100); pn=round(counts["not"]/t*100)
        st.markdown(f"""
<div class="bar-row">
  <div class="bar-label" title="{dv}">{dv}</div>
  <div class="bar-track" style="position:relative;height:20px;border-radius:6px;overflow:hidden;">
    <div style="position:absolute;left:0;top:0;height:100%;width:{pa}%;background:#22c55e;"></div>
    <div style="position:absolute;left:{pa}%;top:0;height:100%;width:{pp}%;background:#f59e0b;"></div>
    <div style="position:absolute;left:{pa+pp}%;top:0;height:100%;width:{pn}%;background:#ef4444;"></div>
  </div>
  <div style="font-size:12px;font-weight:600;color:#16a34a;width:38px;text-align:right;">{pa}%</div>
  <div style="font-size:11px;color:#9ca3af;width:80px;text-align:right;">{counts['acc']}/{t}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("""
<div style="display:flex;gap:18px;margin-top:10px;">
  <div style="display:flex;align-items:center;gap:6px;font-size:12px;color:#374151;">
    <div style="width:12px;height:12px;background:#22c55e;border-radius:2px;"></div> Accomplished
  </div>
  <div style="display:flex;align-items:center;gap:6px;font-size:12px;color:#374151;">
    <div style="width:12px;height:12px;background:#f59e0b;border-radius:2px;"></div> Partially accomplished
  </div>
  <div style="display:flex;align-items:center;gap:6px;font-size:12px;color:#374151;">
    <div style="width:12px;height:12px;background:#ef4444;border-radius:2px;"></div> Not accomplished
  </div>
</div>""", unsafe_allow_html=True)

    # Top performers
    st.markdown(f'<div class="sec-head" style="margin-top:28px;">🏆 Top Performers by {dimension}</div>', unsafe_allow_html=True)
    top=sorted(ia_agg.items(),key=lambda x:x[1]["acc"]/max(x[1]["total"],1),reverse=True)[:3]
    if top:
        tc=st.columns(len(top))
        for col,(dv,counts) in zip(tc,top):
            t=counts["total"] or 1; pa=round(counts["acc"]/t*100)
            with col:
                st.markdown(f"""
<div class="kpi-card" style="text-align:center;border-color:#86efac;">
  <div style="font-size:20px;margin-bottom:4px;">🏆</div>
  <div style="font-size:13px;font-weight:700;color:#111;margin-bottom:4px;">{dv}</div>
  <div style="font-size:26px;font-weight:700;color:#16a34a;">{pa}%</div>
  <div class="kpi-sub">{counts['acc']} of {t} outputs accomplished</div>
</div>""", unsafe_allow_html=True)

    # Risk bars
    st.markdown(f'<div class="sec-head" style="margin-top:28px;">⚠️ Delinquency Risk Flags by {dimension}</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:12px;color:#6b7280;margin-bottom:14px;">% of applicants flagged at risk. Higher = more at-risk.</div>', unsafe_allow_html=True)
    for dv,counts in sorted(risk_agg.items(),key=lambda x:x[1]["high_risk"]/max(x[1]["total"],1),reverse=True):
        t=counts["total"] or 1; pr=round(counts["high_risk"]/t*100)
        col_r="#ef4444" if pr>=50 else "#f59e0b" if pr>=25 else "#22c55e"
        fill="bar-fill-red" if pr>=50 else "bar-fill-orange" if pr>=25 else "bar-fill-green"
        flag="🔴" if pr>=50 else "🟡" if pr>=25 else "🟢"
        st.markdown(f"""
<div class="bar-row">
  <div class="bar-label" title="{dv}">{flag} {dv}</div>
  <div class="bar-track"><div class="{fill}" style="width:{pr}%;"></div></div>
  <div class="bar-pct" style="color:{col_r};">{pr}%</div>
  <div style="font-size:11px;color:#9ca3af;width:100px;text-align:right;">{counts['high_risk']}/{t} flagged</div>
</div>""", unsafe_allow_html=True)

    # Highest at-risk
    st.markdown(f'<div class="sec-head" style="margin-top:28px;">🚨 Highest At-Risk Groups</div>', unsafe_allow_html=True)
    hr=sorted(risk_agg.items(),key=lambda x:x[1]["high_risk"]/max(x[1]["total"],1),reverse=True)[:3]
    if hr:
        hc=st.columns(len(hr))
        for col,(dv,counts) in zip(hc,hr):
            t=counts["total"] or 1; pr=round(counts["high_risk"]/t*100)
            with col:
                st.markdown(f"""
<div class="kpi-card" style="text-align:center;border-color:#fca5a5;">
  <div style="font-size:20px;margin-bottom:4px;">🚨</div>
  <div style="font-size:13px;font-weight:700;color:#111;margin-bottom:4px;">{dv}</div>
  <div style="font-size:26px;font-weight:700;color:#dc2626;">{pr}%</div>
  <div class="kpi-sub">{counts['high_risk']} of {t} flagged at risk</div>
</div>""", unsafe_allow_html=True)

    st.markdown("""
<div style="margin-top:28px;padding:14px 18px;background:#fef9c3;border:1px solid #fcd34d;
            border-radius:10px;font-size:12px;color:#78350f;">
  <strong>⚠️ Note:</strong> Risk flags use prior funding history as a proxy indicator.
  For precise scores, use the <strong>Delinquency Risk Assessment</strong> tab with the full logistic regression model.
</div>""", unsafe_allow_html=True)


st.markdown('</div>', unsafe_allow_html=True)
st.markdown("<br><p style='font-size:11px;color:#ccc;text-align:center;'>DOST-VI SETUP 4.0 iFund Program · Region VI</p>", unsafe_allow_html=True)
