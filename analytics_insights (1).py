"""
Analytics & Insights Dashboard
DOST SETUP 4.0 iFund Program — Region VI

Tabs:
  1. Program Overview
  2. Impact Assessment
  3. Delinquency Risk Assessment
  4. Program Insights
"""

import streamlit as st
import numpy as np
import pickle
import os
import plotly.graph_objects as go
import json

# ── Page config ───────────────────────────────────────────────────────────────
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

  /* Hide default Streamlit chrome */
  [data-testid="stSidebar"]        { display: none; }
  [data-testid="collapsedControl"] { display: none; }
  [data-testid="stDecoration"]     { display: none; }
  header { visibility: hidden; }

  /* Page shell */
  .block-container { padding: 0 !important; max-width: 100% !important; }

  /* ── Top bar ── */
  .topbar {
    display: flex; align-items: center; justify-content: space-between;
    background: #fff; border-bottom: 1px solid #e5e7eb;
    padding: 0 28px; height: 52px; position: sticky; top: 0; z-index: 100;
  }
  .topbar-title { font-size: 15px; font-weight: 700; color: #111; }
  .topbar-right { display: flex; align-items: center; gap: 14px; }
  .province-pill {
    display: flex; align-items: center; gap: 6px;
    border: 1px solid #e5e7eb; border-radius: 20px;
    padding: 4px 12px; font-size: 12px; color: #374151; cursor: pointer;
    background: #fff;
  }

  /* ── Nav tabs ── */
  .navtabs {
    display: flex; align-items: flex-end; gap: 0;
    background: #fff; border-bottom: 1px solid #e5e7eb;
    padding: 0 28px;
  }
  .navtab {
    display: flex; align-items: center; gap: 7px;
    padding: 13px 18px 11px 18px;
    font-size: 13px; font-weight: 500; color: #6b7280;
    border-bottom: 2px solid transparent;
    cursor: pointer; white-space: nowrap; text-decoration: none;
    transition: color .15s;
    background: none; border-left: none; border-right: none; border-top: none;
  }
  .navtab:hover { color: #1d4ed8; }
  .navtab.active {
    color: #1d4ed8; border-bottom: 2px solid #1d4ed8; font-weight: 600;
  }
  .navtab svg { width: 15px; height: 15px; }

  /* ── Content area ── */
  .content { padding: 28px 32px 60px 32px; }

  /* ── Metric cards ── */
  .kpi-row { display: flex; gap: 14px; margin-bottom: 24px; }
  .kpi-card {
    flex: 1; background: #fff; border: 1px solid #e5e7eb;
    border-radius: 12px; padding: 18px 20px;
  }
  .kpi-label { font-size: 11px; color: #9ca3af; font-weight: 600;
                text-transform: uppercase; letter-spacing: .06em; margin-bottom: 6px; }
  .kpi-value { font-size: 28px; font-weight: 700; line-height: 1; color: #111; }
  .kpi-sub   { font-size: 12px; color: #9ca3af; margin-top: 4px; }
  .kpi-green  { color: #16a34a; }
  .kpi-orange { color: #d97706; }
  .kpi-red    { color: #dc2626; }
  .kpi-blue   { color: #1d4ed8; }

  /* ── Section heading ── */
  .sec-head {
    font-size: 11px; font-weight: 700; color: #6b7280;
    letter-spacing: .08em; text-transform: uppercase; margin: 24px 0 12px 0;
  }

  /* ── IA output cards ── */
  .metrics-row { display: flex; gap: 10px; margin: 18px 0 20px 0; }
  .metric-card {
    flex: 1; background: #f9fafb; border-radius: 10px;
    padding: 12px 14px; border: 1px solid #e5e7eb;
  }
  .metric-label { font-size: 11px; color: #9ca3af; font-weight: 500; margin-bottom: 4px; }
  .metric-value { font-size: 26px; font-weight: 700; line-height: 1.1; }
  .metric-sub   { font-size: 11px; color: #9ca3af; margin-top: 2px; }
  .mv-default { color: #1a1a1a; }
  .mv-green   { color: #16a34a; }
  .mv-orange  { color: #d97706; }
  .mv-red     { color: #dc2626; }

  .output-grid { display: flex; gap: 12px; margin-bottom: 12px; }
  .output-card {
    flex: 1; border-radius: 10px; padding: 14px 16px;
    border: 1.5px solid #e5e7eb; background: #fff; min-width: 0;
  }
  .output-card.red-border    { border-color: #fca5a5; }
  .output-card.green-border  { border-color: #86efac; }
  .output-card.orange-border { border-color: #fcd34d; }

  .card-type  { font-size: 10px; font-weight: 700; color: #9ca3af;
                letter-spacing: .06em; text-transform: uppercase; margin-bottom: 5px; }
  .card-title { font-size: 13px; font-weight: 700; color: #111;
                margin-bottom: 10px; line-height: 1.3; }
  .trow       { display: flex; justify-content: space-between;
                font-size: 12px; color: #374151; margin-bottom: 2px; }
  .trow-val   { font-weight: 600; }

  .progress-track { background: #e5e7eb; border-radius: 4px; height: 5px;
                    margin: 8px 0; overflow: hidden; }
  .progress-fill-green  { background: #22c55e; height: 5px; border-radius: 4px; }
  .progress-fill-red    { background: #ef4444; height: 5px; border-radius: 4px; }
  .progress-fill-orange { background: #f59e0b; height: 5px; border-radius: 4px; }

  .verdict-row { display: flex; justify-content: space-between;
                 align-items: center; margin: 8px 0 6px 0; }
  .badge-accomplished     { background:#dcfce7; color:#15803d; font-size:11px;
                             font-weight:600; padding:3px 10px; border-radius:20px; }
  .badge-partial          { background:#fef9c3; color:#a16207; font-size:11px;
                             font-weight:600; padding:3px 10px; border-radius:20px; }
  .badge-not-accomplished { background:#fee2e2; color:#b91c1c; font-size:11px;
                             font-weight:600; padding:3px 10px; border-radius:20px; }
  .pct-label  { font-size: 11px; color: #9ca3af; }
  .card-note  { font-size: 11px; color: #6b7280; margin-top: 8px; line-height: 1.4; }

  .nq-actual-label { font-size:10px; font-weight:600; color:#9ca3af;
                      text-transform:uppercase; letter-spacing:.05em; margin:8px 0 3px 0; }
  .nq-actual-text  { font-size:12px; color:#374151; line-height:1.4; margin-bottom:10px; }
  .verdict-label-inline { font-size:11px; color:#6b7280; font-weight:500; }

  .overall-row {
    display:flex; justify-content:space-between; align-items:center;
    border:1.5px solid #e5e7eb; border-radius:10px;
    padding:12px 16px; margin-top:20px; background:#f9fafb;
  }
  .overall-label        { font-size:13px; font-weight:600; color:#374151; }
  .overall-badge-green  { color:#16a34a; font-size:13px; font-weight:600; }
  .overall-badge-orange { color:#d97706; font-size:13px; font-weight:600; }
  .overall-badge-red    { color:#dc2626; font-size:13px; font-weight:600; }

  /* ── Insights bar chart ── */
  .bar-row { display:flex; align-items:center; gap:10px; margin-bottom:8px; }
  .bar-label { font-size:12px; color:#374151; width:180px; flex-shrink:0;
               white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .bar-track { flex:1; background:#f3f4f6; border-radius:4px; height:16px; overflow:hidden; }
  .bar-fill-green  { background:#22c55e; height:16px; border-radius:4px; }
  .bar-fill-orange { background:#f59e0b; height:16px; border-radius:4px; }
  .bar-fill-red    { background:#ef4444; height:16px; border-radius:4px; }
  .bar-fill-blue   { background:#3b82f6; height:16px; border-radius:4px; }
  .bar-pct { font-size:12px; font-weight:600; color:#374151; width:38px;
              text-align:right; flex-shrink:0; }

  /* ── Risk card ── */
  .risk-card {
    border-radius:12px; padding:16px 20px; text-align:center;
    border:1.5px solid #e5e7eb;
  }

  /* ── Selectbox label hide ── */
  .stSelectbox > label { display: none !important; }
  div[data-baseweb="select"] { border-radius: 8px !important; }

  /* ── Overview MSME table ── */
  .msme-table { width:100%; border-collapse:collapse; font-size:13px; }
  .msme-table th {
    text-align:left; font-size:11px; font-weight:700; color:#6b7280;
    text-transform:uppercase; letter-spacing:.06em;
    border-bottom:2px solid #e5e7eb; padding:8px 12px;
  }
  .msme-table td { padding:10px 12px; border-bottom:1px solid #f3f4f6; color:#374151; }
  .msme-table tr:hover td { background:#f9fafb; }

  /* period badge */
  .period-badge {
    display:inline-block; background:#dbeafe; color:#1d4ed8;
    font-size:11px; font-weight:600; padding:3px 10px; border-radius:20px;
    float:right; margin-top:2px;
  }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════════════════════════

from demo_data import DEMO_REPORTS

def supabase_configured():
    url = st.secrets.get("SUPABASE_URL", os.environ.get("SUPABASE_URL", ""))
    key = st.secrets.get("SUPABASE_KEY", os.environ.get("SUPABASE_KEY", ""))
    return bool(url and key)

@st.cache_data(ttl=300, show_spinner="Loading data…")
def load_reports():
    from supabase import create_client
    url = st.secrets.get("SUPABASE_URL", os.environ.get("SUPABASE_URL", ""))
    key = st.secrets.get("SUPABASE_KEY", os.environ.get("SUPABASE_KEY", ""))
    supabase = create_client(url, key)
    msmes_resp     = supabase.table("msmes").select("*").execute()
    semesters_resp = supabase.table("semesters").select("*").order("sort_order").execute()
    quant_resp     = supabase.table("quantifiable_outputs").select("*").order("sort_order").execute()
    nonquant_resp  = supabase.table("non_quantifiable_outputs").select("*").order("sort_order").execute()
    msmes        = msmes_resp.data or []
    semesters    = semesters_resp.data or []
    quant_rows   = quant_resp.data or []
    nonquant_rows= nonquant_resp.data or []
    quant_by_sem, nonquant_by_sem, semesters_by_msme = {}, {}, {}
    for row in quant_rows:
        quant_by_sem.setdefault(row["semester_id"], []).append({k: row.get(k) for k in
            ["title","target_val","target_unit","actual_val","actual_unit","verdict","pct","note"]})
    for row in nonquant_rows:
        nonquant_by_sem.setdefault(row["semester_id"], []).append({k: row.get(k) for k in
            ["title","actual","default_verdict"]})
    for sem in semesters:
        semesters_by_msme.setdefault(sem["msme_id"], []).append(sem)
    reports = {}
    for msme in msmes:
        sem_dict = {}
        for sem in semesters_by_msme.get(msme["id"], []):
            sem_dict[sem["name"]] = {
                "period_badge": sem.get("period_badge", sem["name"]),
                "quantifiable": quant_by_sem.get(sem["id"], []),
                "non_quantifiable": nonquant_by_sem.get(sem["id"], []),
                "overall": sem.get("overall", "not accomplished"),
            }
        reports[msme["name"]] = {"address": msme.get("address",""), "semesters": sem_dict}
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

# ── MOCK_DB for delinquency (same as original app.py) ──────────────────────
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
    with open(MODEL_PATH, "rb") as f:
        orange_model = pickle.load(f)
    return orange_model.skl_model

try:
    skl_model = load_model()
    model_ok  = True
except Exception as _model_err:
    skl_model = None
    model_ok  = False
    _model_err_msg = str(_model_err)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

VERDICT_OPTIONS = ["Accomplished", "Partially accomplished", "Not accomplished"]

def verdict_badge_cls(v):
    v = v.lower()
    if v == "accomplished":        return "badge-accomplished",     "✓ Accomplished"
    if v == "partially accomplished": return "badge-partial",       "— Partially accomplished"
    return                                   "badge-not-accomplished","✕ Not accomplished"

def badge_html(v):
    cls, label = verdict_badge_cls(v)
    return f'<span class="{cls}">{label}</span>'

def progress_color(v):
    v = v.lower()
    if v == "accomplished":           return "progress-fill-green"
    if v == "partially accomplished": return "progress-fill-orange"
    return "progress-fill-red"

def card_border(v):
    v = v.lower()
    if v == "accomplished":           return "green-border"
    if v == "partially accomplished": return "orange-border"
    return "red-border"

def default_verdict_index(dv):
    dv = dv.lower()
    if dv == "accomplished":           return 0
    if dv == "partially accomplished": return 1
    return 2

def build_feature_vector(year, cost_raw, province, sector, ownership, size, prior_funding):
    X = [cost_raw / 1_000_000, float(year)]
    X += [1 if province == p else 0 for p in PROVINCES]
    X += [1 if sector   == s else 0 for s in SECTORS]
    X += [1 if ownership== o else 0 for o in OWNERSHIPS]
    X += [1 if size     == s else 0 for s in SIZES]
    X += [1 if prior_funding == "No"  else 0]
    X += [1 if prior_funding == "Yes" else 0]
    return np.array(X, dtype=float).reshape(1, -1)

def get_risk_tier(pct):
    if pct <= 30: return "Low Risk",    "🟢","#EAF3DE","#97C459","#2B5C0A"
    if pct <= 50: return "Medium Risk", "🟡","#FAEEDA","#EF9F27","#7A4209"
    if pct <= 70: return "High Risk",   "🟠","#FAECE7","#F0997B","#7A2A0A"
    return             "Critical",   "🔴","#FCEBEB","#F09595","#6B1010"

def result_card(label, value, bg, border, text_color):
    st.markdown(
        f"""<div style="background:{bg};border:1.5px solid {border};border-radius:12px;
                        padding:16px 20px;text-align:center;">
                <div style="font-size:12px;font-weight:500;color:#666;text-transform:uppercase;
                            letter-spacing:0.05em;margin-bottom:6px;">{label}</div>
                <div style="font-size:22px;font-weight:600;color:{text_color};">{value}</div>
            </div>""",
        unsafe_allow_html=True,
    )

def ia_summary_stats():
    """Aggregate IA stats across all MSMEs and semesters."""
    total = acc = partial = not_acc = msme_count = sem_count = 0
    msme_count = len(REPORTS)
    for msme_data in REPORTS.values():
        for sem_data in msme_data["semesters"].values():
            sem_count += 1
            for o in sem_data["quantifiable"] + sem_data["non_quantifiable"]:
                v = o.get("verdict", o.get("default_verdict","not accomplished")).lower()
                total += 1
                if v == "accomplished":           acc += 1
                elif v == "partially accomplished": partial += 1
                else:                               not_acc += 1
    return msme_count, sem_count, total, acc, partial, not_acc

def per_msme_latest_overall():
    """Return list of (msme_name, latest_semester, overall_verdict) sorted by name."""
    rows = []
    for name, data in REPORTS.items():
        sems = list(data["semesters"].items())
        if sems:
            sem_name, sem_data = sems[-1]
            rows.append((name, sem_name, sem_data["overall"], data.get("address","")))
    return rows

def insights_by_dimension(dimension: str):
    """
    Returns dict: { dimension_value: {"acc":n,"partial":n,"not":n,"total":n} }
    Only works on IA REPORTS data. Dimension = "province" or "sector" etc.
    We infer province from address keywords for demo data.
    """
    # For demo data, we map MSME name → province via MOCK_DB lookup
    name_to_province = {r["name"]: r["province"] for r in MOCK_DB}
    name_to_sector   = {r["name"]: r["sector"]   for r in MOCK_DB}
    name_to_ownership= {r["name"]: r["ownership"] for r in MOCK_DB}
    name_to_size     = {r["name"]: r["size"]      for r in MOCK_DB}

    agg = {}
    for msme_name, msme_data in REPORTS.items():
        if dimension == "Province":
            dim_val = name_to_province.get(msme_name, "Unknown")
        elif dimension == "Sector":
            dim_val = name_to_sector.get(msme_name, "Unknown")
        elif dimension == "Ownership":
            dim_val = name_to_ownership.get(msme_name, "Unknown")
        elif dimension == "Enterprise Size":
            dim_val = name_to_size.get(msme_name, "Unknown").capitalize()
        else:
            dim_val = "Unknown"

        if dim_val not in agg:
            agg[dim_val] = {"acc":0,"partial":0,"not":0,"total":0}
        for sem_data in msme_data["semesters"].values():
            for o in sem_data["quantifiable"] + sem_data["non_quantifiable"]:
                v = o.get("verdict", o.get("default_verdict","not accomplished")).lower()
                agg[dim_val]["total"] += 1
                if v == "accomplished":              agg[dim_val]["acc"]     += 1
                elif v == "partially accomplished":  agg[dim_val]["partial"] += 1
                else:                                agg[dim_val]["not"]     += 1
    return agg

def delinquency_risk_by_dimension(dimension: str):
    """Aggregate MOCK_DB by dimension, count high-risk flags (simulated)."""
    # Simulate risk: prior_funding=No → higher risk proxy
    agg = {}
    for r in MOCK_DB:
        if dimension == "Province":     dim_val = r["province"]
        elif dimension == "Sector":     dim_val = r["sector"]
        elif dimension == "Ownership":  dim_val = r["ownership"]
        elif dimension == "Enterprise Size": dim_val = r["size"].capitalize()
        else: dim_val = "Unknown"

        if dim_val not in agg:
            agg[dim_val] = {"high_risk":0,"total":0}
        agg[dim_val]["total"] += 1
        # Proxy: no prior funding = at risk
        if r["prior_funding"] == "No":
            agg[dim_val]["high_risk"] += 1
    return agg


# ── Region VI Province GeoJSON (approximate polygons) ──────────────────────
REGION_VI_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "id": "Aklan",
            "properties": {"name": "Aklan"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[122.05,11.50],[122.65,11.50],[122.75,11.80],[122.60,12.05],
                                  [122.30,12.10],[122.05,11.95],[121.95,11.70],[122.05,11.50]]]
            }
        },
        {
            "type": "Feature",
            "id": "Antique",
            "properties": {"name": "Antique"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[121.85,10.30],[122.05,10.30],[122.15,10.65],[122.10,11.15],
                                  [121.95,11.45],[121.70,11.35],[121.65,10.90],[121.75,10.50],[121.85,10.30]]]
            }
        },
        {
            "type": "Feature",
            "id": "Capiz",
            "properties": {"name": "Capiz"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[122.45,11.20],[122.95,11.25],[123.10,11.50],[122.90,11.80],
                                  [122.60,11.80],[122.35,11.55],[122.30,11.35],[122.45,11.20]]]
            }
        },
        {
            "type": "Feature",
            "id": "Guimaras",
            "properties": {"name": "Guimaras"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[122.50,10.50],[122.75,10.45],[122.85,10.65],[122.70,10.85],
                                  [122.50,10.85],[122.38,10.70],[122.50,10.50]]]
            }
        },
        {
            "type": "Feature",
            "id": "Iloilo",
            "properties": {"name": "Iloilo"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[122.05,10.60],[122.55,10.55],[122.80,10.80],[122.85,11.10],
                                  [122.65,11.25],[122.25,11.25],[122.00,11.05],[121.90,10.80],[122.05,10.60]]]
            }
        },
        {
            "type": "Feature",
            "id": "Negros",
            "properties": {"name": "Negros"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[122.50,9.40],[123.10,9.40],[123.30,9.80],[123.20,10.30],
                                  [122.90,10.60],[122.55,10.70],[122.35,10.40],[122.30,9.90],[122.50,9.40]]]
            }
        },
    ]
}

PROVINCE_CENTERS = {
    "Aklan":    (11.78, 122.37),
    "Antique":  (10.88, 121.95),
    "Capiz":    (11.45, 122.72),
    "Guimaras": (10.65, 122.62),
    "Iloilo":   (10.90, 122.45),
    "Negros":   (10.00, 122.90),
}

def build_choropleth(metric: str = "accomplishment", title: str = "Province Map"):
    """
    Build a Plotly choropleth for Region VI provinces.
    metric: 'accomplishment' | 'risk'
    """
    ia_agg   = insights_by_dimension("Province")
    risk_agg = delinquency_risk_by_dimension("Province")

    provinces = list(PROVINCE_CENTERS.keys())
    values, hover_texts, colors = [], [], []

    if metric == "accomplishment":
        colorscale = [[0,"#fee2e2"],[0.5,"#fef9c3"],[1,"#dcfce7"]]
        colorbar_title = "Accomplishment %"
        for p in provinces:
            counts = ia_agg.get(p, {"acc":0,"total":1})
            total  = counts["total"] or 1
            pct    = round(counts["acc"] / total * 100)
            values.append(pct)
            hover_texts.append(
                f"<b>{p}</b><br>Accomplished: {counts['acc']}/{total} ({pct}%)"
            )
    else:  # risk
        colorscale = [[0,"#dcfce7"],[0.5,"#fef9c3"],[1,"#fee2e2"]]
        colorbar_title = "At-Risk %"
        for p in provinces:
            counts = risk_agg.get(p, {"high_risk":0,"total":1})
            total  = counts["total"] or 1
            pct    = round(counts["high_risk"] / total * 100)
            values.append(pct)
            hover_texts.append(
                f"<b>{p}</b><br>At-Risk: {counts['high_risk']}/{total} ({pct}%)"
            )

    fig = go.Figure(go.Choropleth(
        geojson=REGION_VI_GEOJSON,
        locations=provinces,
        z=values,
        text=hover_texts,
        hoverinfo="text",
        colorscale=colorscale,
        zmin=0, zmax=100,
        marker_line_color="#ffffff",
        marker_line_width=1.5,
        colorbar=dict(
            title=dict(text=colorbar_title, font=dict(size=11, color="#6b7280")),
            thickness=12,
            len=0.6,
            tickfont=dict(size=10, color="#6b7280"),
            ticksuffix="%",
        ),
        featureidkey="id",
    ))

    # Province name annotations
    for p, (lat, lon) in PROVINCE_CENTERS.items():
        idx = provinces.index(p)
        fig.add_scattergeo(
            lat=[lat], lon=[lon],
            text=[f"<b>{p}</b><br>{values[idx]}%"],
            mode="text",
            textfont=dict(size=10, color="#1a1a1a"),
            showlegend=False,
            hoverinfo="skip",
        )

    fig.update_geos(
        visible=False,
        fitbounds="locations",
        resolution=50,
        bgcolor="rgba(0,0,0,0)",
        landcolor="#f9fafb",
        oceancolor="#e0f2fe",
        lakecolor="#e0f2fe",
        showocean=True,
        showlakes=True,
    )
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color="#111", family="Inter"), x=0, xref="paper"),
        margin=dict(l=0, r=0, t=36, b=0),
        height=320,
        paper_bgcolor="rgba(0,0,0,0)",
        geo=dict(bgcolor="rgba(0,0,0,0)"),
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# TOP BAR + NAV
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="topbar">
  <span class="topbar-title">Analytics &amp; Insights</span>
  <div class="topbar-right">
    <div class="province-pill">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
        <circle cx="12" cy="9" r="2.5"/>
      </svg>
      All Provinces ▾
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# Tab state
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Program Overview"

TABS = [
    ("Program Overview",          "M12 20h9M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"),
    ("Impact Assessment",         "M3 3h18v18H3zM9 9h6M9 12h6M9 15h4"),
    ("Delinquency Risk",          "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"),
    ("Program Insights",          "M18 20V10M12 20V4M6 20v-6"),
]

tab_html = '<div class="navtabs">'
for label, _ in TABS:
    active_cls = "active" if st.session_state.active_tab == label else ""
    tab_html += f'<span class="navtab {active_cls}" id="tab-{label.replace(" ","-")}">{label}</span>'
tab_html += "</div>"
st.markdown(tab_html, unsafe_allow_html=True)

# Streamlit tab buttons (invisible, positioned under nav)
cols = st.columns(len(TABS))
for i, (label, _) in enumerate(TABS):
    with cols[i]:
        if st.button(label, key=f"navbtn_{i}", use_container_width=True,
                     help=label):
            st.session_state.active_tab = label
            st.rerun()

st.markdown("<style>[data-testid='stHorizontalBlock'] button { opacity:0; height:2px; padding:0; margin:0; border:none; } </style>", unsafe_allow_html=True)

tab = st.session_state.active_tab
st.markdown('<div class="content">', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — PROGRAM OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if tab == "Program Overview":
    msme_count, sem_count, total_out, acc, partial, not_acc = ia_summary_stats()
    pct_acc = round(acc/total_out*100) if total_out else 0

    st.markdown(f"""
    <div class="kpi-row">
      <div class="kpi-card">
        <div class="kpi-label">Total MSMEs</div>
        <div class="kpi-value kpi-blue">{msme_count}</div>
        <div class="kpi-sub">enrolled in program</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Semesters Assessed</div>
        <div class="kpi-value">{sem_count}</div>
        <div class="kpi-sub">across all MSMEs</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Outputs Accomplished</div>
        <div class="kpi-value kpi-green">{acc}</div>
        <div class="kpi-sub">{pct_acc}% of {total_out} total outputs</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Partially Accomplished</div>
        <div class="kpi-value kpi-orange">{partial}</div>
        <div class="kpi-sub">of {total_out} total outputs</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Not Accomplished</div>
        <div class="kpi-value kpi-red">{not_acc}</div>
        <div class="kpi-sub">of {total_out} total outputs</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">At-Risk Applicants</div>
        <div class="kpi-value kpi-red">{sum(1 for r in MOCK_DB if r['prior_funding']=='No')}</div>
        <div class="kpi-sub">no prior funding (proxy)</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec-head">MSME Status — Latest Semester</div>', unsafe_allow_html=True)
    rows = per_msme_latest_overall()

    table_html = """
    <table class="msme-table">
      <thead>
        <tr>
          <th>MSME Name</th>
          <th>Address</th>
          <th>Latest Semester</th>
          <th>Overall Verdict</th>
        </tr>
      </thead>
      <tbody>
    """
    for name, sem, overall, addr in rows:
        cls, lbl = verdict_badge_cls(overall)
        table_html += f"""
        <tr>
          <td><strong>{name}</strong></td>
          <td style="color:#9ca3af;font-size:12px;">{addr}</td>
          <td style="font-size:12px;">{sem}</td>
          <td><span class="{cls}">{lbl}</span></td>
        </tr>"""
    table_html += "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)

    st.markdown('<div class="sec-head" style="margin-top:28px;">Delinquency Risk Pool</div>', unsafe_allow_html=True)
    risk_cols = st.columns(4)
    tier_counts = {"Low Risk":0,"Medium Risk":0,"High Risk":0,"Critical":0}
    # Simulate risk buckets from cost distribution
    for r in MOCK_DB:
        pf = 1 if r["prior_funding"]=="Yes" else 0
        cost_m = r["cost"]/1_000_000
        proxy_risk = int(max(0, min(100, (1-pf)*60 + cost_m*5)))
        tier,*_ = get_risk_tier(proxy_risk)
        tier_counts[tier] += 1
    colors = {"Low Risk":"#16a34a","Medium Risk":"#d97706","High Risk":"#ea580c","Critical":"#dc2626"}
    icons  = {"Low Risk":"🟢","Medium Risk":"🟡","High Risk":"🟠","Critical":"🔴"}
    for col, (tier, cnt) in zip(risk_cols, tier_counts.items()):
        with col:
            st.markdown(f"""
            <div class="kpi-card" style="text-align:center;">
              <div style="font-size:22px;">{icons[tier]}</div>
              <div style="font-size:11px;font-weight:700;color:{colors[tier]};
                          text-transform:uppercase;letter-spacing:.05em;margin:4px 0;">{tier}</div>
              <div class="kpi-value" style="color:{colors[tier]};">{cnt}</div>
              <div class="kpi-sub">applicants</div>
            </div>""", unsafe_allow_html=True)

    # ── Province Choropleth Maps ─────────────────────────────────────────────
    st.markdown('<div class="sec-head" style="margin-top:28px;">Province-Level Distribution — Region VI</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:12px;color:#6b7280;margin-bottom:14px;">Geographic breakdown of accomplishment rates and delinquency risk across Western Visayas provinces.</div>', unsafe_allow_html=True)

    map_c1, map_c2 = st.columns(2)
    with map_c1:
        st.plotly_chart(
            build_choropleth("accomplishment", "IA Accomplishment Rate by Province"),
            use_container_width=True, config={"displayModeBar": False}
        )
    with map_c2:
        st.plotly_chart(
            build_choropleth("risk", "At-Risk Applicants by Province"),
            use_container_width=True, config={"displayModeBar": False}
        )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — IMPACT ASSESSMENT (original IA app)
# ══════════════════════════════════════════════════════════════════════════════
elif tab == "Impact Assessment":
    st.markdown('<div style="font-size:18px;font-weight:700;color:#1a1a1a;margin-bottom:2px;">Impact Assessment</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:12px;color:#888;margin-bottom:14px;">DOST SETUP 4.0 iFund Program — Region VI</div>', unsafe_allow_html=True)

    msme_names = list(REPORTS.keys())
    sel_msme   = st.selectbox("MSME", msme_names, label_visibility="collapsed")
    msme_data  = REPORTS[sel_msme]
    sem_names  = list(msme_data["semesters"].keys())
    sel_sem    = st.selectbox("Semester", sem_names, label_visibility="collapsed")
    sem_data   = msme_data["semesters"][sel_sem]

    st.markdown(f'<div class="period-badge">{sem_data["period_badge"]}</div>', unsafe_allow_html=True)
    st.markdown("<div style='clear:both;height:4px;'></div>", unsafe_allow_html=True)

    quant_outputs    = sem_data["quantifiable"]
    nonquant_outputs = sem_data["non_quantifiable"]
    total_outputs    = len(quant_outputs) + len(nonquant_outputs)
    accomplished = partial = not_acc = 0
    for o in quant_outputs:
        v = o["verdict"].lower()
        if v=="accomplished": accomplished+=1
        elif v=="partially accomplished": partial+=1
        else: not_acc+=1
    for o in nonquant_outputs:
        v = o["default_verdict"].lower()
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
        pairs = [quant_outputs[i:i+2] for i in range(0, len(quant_outputs), 2)]
        for pair in pairs:
            cols = st.columns(2)
            for col, item in zip(cols, pair):
                with col:
                    border_cls = card_border(item["verdict"])
                    prog_cls   = progress_color(item["verdict"])
                    pct        = item["pct"]
                    target_row = f'<div class="trow"><span>Target</span><span class="trow-val">{item["target_val"]} {item["target_unit"]}</span></div>' if item["target_val"] else ""
                    actual_row = f'<div class="trow"><span>Actual</span><span class="trow-val">{item["actual_val"]} {item["actual_unit"]}</span></div>' if item["actual_val"] else ""
                    note_html  = f'<div class="card-note">{item["note"]}</div>' if item["note"] else ""
                    st.markdown(f"""
<div class="output-card {border_cls}">
  <div class="card-type">Quantifiable</div>
  <div class="card-title">{item['title']}</div>
  {target_row}{actual_row}
  <div class="progress-track"><div class="{prog_cls}" style="width:{pct}%;"></div></div>
  <div class="verdict-row">{badge_html(item['verdict'])}<span class="pct-label">{pct}% of target</span></div>
  {note_html}
</div>""", unsafe_allow_html=True)

    if nonquant_outputs:
        st.markdown('<div class="sec-head">Non-Quantifiable Outputs</div>', unsafe_allow_html=True)
        if "nq_verdicts" not in st.session_state:
            st.session_state["nq_verdicts"] = {}
        state_key_prefix = f"{sel_msme}_{sel_sem}"
        nq_pairs = [nonquant_outputs[i:i+2] for i in range(0, len(nonquant_outputs), 2)]
        for pair_idx, pair in enumerate(nq_pairs):
            cols = st.columns(2)
            for col_idx, (col, item) in enumerate(zip(cols, pair)):
                with col:
                    state_key   = f"{state_key_prefix}_nq_{pair_idx}_{col_idx}"
                    default_idx = default_verdict_index(item["default_verdict"])
                    chosen      = st.selectbox(f"Verdict for: {item['title'][:30]}",
                                               VERDICT_OPTIONS, index=default_idx,
                                               key=state_key, label_visibility="collapsed")
                    border_cls = card_border(chosen)
                    st.markdown(f"""
<div class="output-card {border_cls}" style="margin-top:-8px;">
  <div class="card-type">Non-Quantifiable</div>
  <div class="card-title">{item['title']}</div>
  <div class="nq-actual-label">Actual accomplishment</div>
  <div class="nq-actual-text">{item['actual']}</div>
  <div style="display:flex;align-items:center;gap:8px;margin-top:6px;">
    <span class="verdict-label-inline">Verdict (PSTO):</span>
  </div>
</div>""", unsafe_allow_html=True)
                    st.markdown(f'<div style="margin-top:4px;">{badge_html(chosen)}</div>', unsafe_allow_html=True)

    overall = sem_data["overall"]
    if overall.lower() == "accomplished":
        overall_html = '<span class="overall-badge-green">✓ Accomplished</span>'
    elif overall.lower() == "partially accomplished":
        overall_html = '<span class="overall-badge-orange">— Partially accomplished</span>'
    else:
        overall_html = '<span class="overall-badge-red">✕ Not accomplished</span>'
    st.markdown(f"""
<div class="overall-row">
  <div style="display:flex;align-items:center;gap:8px;">
    <span style="font-size:16px;">📊</span>
    <span class="overall-label">Overall semester verdict</span>
  </div>
  {overall_html}
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — DELINQUENCY RISK ASSESSMENT (original app.py)
# ══════════════════════════════════════════════════════════════════════════════
elif tab == "Delinquency Risk":
    st.markdown('<div style="font-size:18px;font-weight:700;color:#1a1a1a;margin-bottom:2px;">MSME Delinquency Risk Assessment</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:12px;color:#888;margin-bottom:14px;">Western Visayas · Loan-funded project screening</div>', unsafe_allow_html=True)

    if not model_ok:
        st.error(f"⚠️ Model could not be loaded.\n\n`{_model_err_msg}`")
        st.stop()

    if "selected_applicant" not in st.session_state:
        st.session_state.selected_applicant = None
    if "raw_query" not in st.session_state:
        st.session_state.raw_query = ""

    st.subheader("Search applicant")
    applicant = st.session_state.selected_applicant

    if applicant:
        col_badge, col_clear = st.columns([5, 1])
        with col_badge:
            st.markdown(f"""
            <div style="background:#F0F4FF;border:1px solid #C7D4F5;border-radius:10px;padding:10px 16px;">
              <span style="font-size:16px;">🏢</span>
              <strong style="margin-left:8px;">{applicant['name']}</strong>
              <span style="font-size:12px;color:#666;margin-left:8px;">{applicant['id']} · Pre-PIS data loaded</span>
            </div>""", unsafe_allow_html=True)
        with col_clear:
            st.markdown("<div style='margin-top:6px'>", unsafe_allow_html=True)
            if st.button("✕ Clear", use_container_width=True):
                st.session_state.selected_applicant = None
                st.session_state.raw_query = ""
                st.rerun()
    else:
        query_input = st.text_input("Search applicant", value=st.session_state.raw_query,
                                    placeholder="Type MSME name or application ID…",
                                    label_visibility="collapsed")
        st.session_state.raw_query = query_input
        if query_input and len(query_input) >= 2:
            q = query_input.lower()
            results = [a for a in MOCK_DB if q in a["name"].lower() or q in a["id"].lower()][:8]
            if results:
                for r in results:
                    col_name, col_btn = st.columns([6,1])
                    with col_name:
                        st.markdown(f"<div style='padding:4px 4px;'>"
                                    f"<span style='font-weight:500;font-size:14px;'>{r['name']}</span>"
                                    f"<span style='font-size:12px;color:#888;margin-left:10px;'>"
                                    f"{r['id']} · {r['province']} · {r['sector']}</span></div>",
                                    unsafe_allow_html=True)
                    with col_btn:
                        if st.button("Select", key=f"delbtn_{r['id']}", use_container_width=True):
                            st.session_state.selected_applicant = next((a for a in MOCK_DB if a["id"]==r["id"]), None)
                            st.session_state.raw_query = ""
                            st.rerun()
            else:
                st.caption("No matching applicants found.")

    st.divider()
    st.subheader("Applicant details")
    if applicant:
        st.caption("Auto-filled from Pre-PIS record. You may adjust before assessing.")
    else:
        st.caption("Select an applicant above to auto-fill, or enter details manually.")

    col1, col2 = st.columns(2)
    with col1:
        year     = st.number_input("Year", min_value=2000, max_value=2030, step=1,
                                   value=int(applicant["year"]) if applicant else 2024)
    with col2:
        cost_raw = st.number_input("Project cost (₱)", min_value=0.0, step=1000.0, format="%.2f",
                                   value=float(applicant["cost"]) if applicant else 150000.0)
    col3, col4 = st.columns(2)
    with col3:
        province = st.selectbox("Province", PROVINCES,
                                index=PROVINCES.index(applicant["province"]) if applicant and applicant["province"] in PROVINCES else 0)
    with col4:
        sector   = st.selectbox("Sector", SECTORS,
                                index=SECTORS.index(applicant["sector"]) if applicant and applicant["sector"] in SECTORS else 0)
    col5, col6, col7 = st.columns(3)
    with col5:
        ownership = st.selectbox("Ownership type", OWNERSHIPS,
                                 index=OWNERSHIPS.index(applicant["ownership"]) if applicant and applicant["ownership"] in OWNERSHIPS else 0)
    with col6:
        size_options = [s.capitalize() for s in SIZES]
        size_val     = applicant["size"].capitalize() if applicant else "Micro"
        size_display = st.selectbox("Enterprise size", size_options,
                                    index=size_options.index(size_val) if size_val in size_options else 0)
        size = size_display.lower()
    with col7:
        prior_val     = applicant["prior_funding"] if applicant else "Yes"
        prior_funding = st.selectbox("Prior funding", ["Yes","No"],
                                     index=["Yes","No"].index(prior_val) if prior_val in ["Yes","No"] else 0)

    st.divider()
    if st.button("Assess delinquency risk", use_container_width=True, type="primary"):
        X = build_feature_vector(year, cost_raw, province, sector, ownership, size, prior_funding)
        try:
            pred_class      = skl_model.predict(X)[0]
            proba           = skl_model.predict_proba(X)[0]
            p_completed     = float(proba[0])
            p_not_completed = float(proba[1])
            delinquency_pct = round(p_not_completed * 100)
            completed_pct   = round(p_completed * 100)
            is_completed    = pred_class == 0.0
            tier_name, tier_icon, bg, border, text_color = get_risk_tier(delinquency_pct)

            st.subheader("Risk assessment result")
            if applicant:
                st.caption(f"Assessment for: **{applicant['name']}** ({applicant['id']})")
            r1, r2 = st.columns(2)
            with r1:
                icon = "✅" if is_completed else "❌"
                text = "Completed" if is_completed else "Not Completed"
                result_card("Predicted outcome", f"{icon} {text}", bg, border, text_color)
            with r2:
                result_card("Delinquency risk tier", f"{tier_icon} {tier_name}", bg, border, text_color)
            st.markdown("")
            st.markdown(f"**Delinquency probability: {delinquency_pct}%**")
            st.progress(delinquency_pct/100,
                        text=f"{tier_icon} {tier_name} — {delinquency_pct}% likelihood of non-completion")
            st.markdown("")
            p1, p2 = st.columns(2)
            with p1: st.metric("✅ Probability of completion",   f"{completed_pct}%")
            with p2: st.metric("❌ Probability of delinquency",  f"{delinquency_pct}%")
            st.markdown("")
            actions = {
                "Low Risk":    ("✅ Safe to approve.",                                     "#EAF3DE","#97C459"),
                "Medium Risk": ("⚠️ Approve with close monitoring.",                      "#FAEEDA","#EF9F27"),
                "High Risk":   ("🚩 Additional review required before approval.",         "#FAECE7","#F0997B"),
                "Critical":    ("🚨 High default risk — escalate to senior review.",      "#FCEBEB","#F09595"),
            }
            action_text, a_bg, a_border = actions[tier_name]
            st.markdown(f"""<div style="background:{a_bg};border:1.5px solid {a_border};border-radius:10px;
                            padding:12px 16px;font-size:14px;font-weight:500;margin-top:4px;">
                    {action_text}</div>""", unsafe_allow_html=True)
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
            st.error(f"Prediction failed. Please check input values.\n\n`{e}`")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — PROGRAM INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════
elif tab == "Program Insights":
    st.markdown('<div style="font-size:18px;font-weight:700;color:#1a1a1a;margin-bottom:2px;">Program Insights</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:12px;color:#888;margin-bottom:18px;">Performance patterns across provinces, sectors, and enterprise types</div>', unsafe_allow_html=True)

    dim_col, _ = st.columns([2, 5])
    with dim_col:
        dimension = st.selectbox("Analyze by", ["Province","Sector","Ownership","Enterprise Size"],
                                 label_visibility="visible")

    ia_agg   = insights_by_dimension(dimension)
    risk_agg = delinquency_risk_by_dimension(dimension)

    # ── Impact Assessment Performance ──────────────────────────────────────
    st.markdown(f'<div class="sec-head">Impact Assessment Performance by {dimension}</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:12px;color:#6b7280;margin-bottom:14px;">Percentage of outputs accomplished per group. Higher is better.</div>', unsafe_allow_html=True)

    if ia_agg:
        sorted_ia = sorted(ia_agg.items(), key=lambda x: x[1]["acc"]/max(x[1]["total"],1), reverse=True)
        for dim_val, counts in sorted_ia:
            total = counts["total"] or 1
            pct_a = round(counts["acc"]/total*100)
            pct_p = round(counts["partial"]/total*100)
            pct_n = round(counts["not"]/total*100)
            st.markdown(f"""
<div class="bar-row">
  <div class="bar-label" title="{dim_val}">{dim_val}</div>
  <div class="bar-track" style="position:relative;height:20px;border-radius:6px;overflow:hidden;">
    <div style="position:absolute;left:0;top:0;height:100%;width:{pct_a}%;background:#22c55e;"></div>
    <div style="position:absolute;left:{pct_a}%;top:0;height:100%;width:{pct_p}%;background:#f59e0b;"></div>
    <div style="position:absolute;left:{pct_a+pct_p}%;top:0;height:100%;width:{pct_n}%;background:#ef4444;"></div>
  </div>
  <div style="font-size:12px;font-weight:600;color:#16a34a;width:38px;text-align:right;">{pct_a}%</div>
  <div style="font-size:11px;color:#9ca3af;width:80px;text-align:right;">{counts['acc']}/{total} outputs</div>
</div>""", unsafe_allow_html=True)

        # Legend
        st.markdown("""
<div style="display:flex;gap:18px;margin-top:10px;margin-bottom:4px;">
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

    # ── Top Performers ──────────────────────────────────────────────────────
    st.markdown(f'<div class="sec-head" style="margin-top:28px;">🏆 Top Performers by {dimension}</div>', unsafe_allow_html=True)
    top = sorted(ia_agg.items(), key=lambda x: x[1]["acc"]/max(x[1]["total"],1), reverse=True)[:3]
    top_cols = st.columns(len(top)) if top else []
    for col, (dim_val, counts) in zip(top_cols, top):
        total = counts["total"] or 1
        pct_a = round(counts["acc"]/total*100)
        with col:
            st.markdown(f"""
<div class="kpi-card" style="text-align:center;border-color:#86efac;">
  <div style="font-size:20px;margin-bottom:4px;">🏆</div>
  <div style="font-size:13px;font-weight:700;color:#111;margin-bottom:4px;">{dim_val}</div>
  <div style="font-size:26px;font-weight:700;color:#16a34a;">{pct_a}%</div>
  <div class="kpi-sub">{counts['acc']} of {total} outputs accomplished</div>
</div>""", unsafe_allow_html=True)

    # ── Delinquency Risk Flags ───────────────────────────────────────────────
    st.markdown(f'<div class="sec-head" style="margin-top:28px;">⚠️ Delinquency Risk Flags by {dimension}</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:12px;color:#6b7280;margin-bottom:14px;">Groups with higher proportions of at-risk applicants (no prior funding). These may need targeted monitoring.</div>', unsafe_allow_html=True)

    if risk_agg:
        sorted_risk = sorted(risk_agg.items(), key=lambda x: x[1]["high_risk"]/max(x[1]["total"],1), reverse=True)
        for dim_val, counts in sorted_risk:
            total = counts["total"] or 1
            pct_r = round(counts["high_risk"]/total*100)
            color = "#ef4444" if pct_r >= 50 else "#f59e0b" if pct_r >= 25 else "#22c55e"
            fill  = "bar-fill-red" if pct_r >= 50 else "bar-fill-orange" if pct_r >= 25 else "bar-fill-green"
            flag  = "🔴" if pct_r >= 50 else "🟡" if pct_r >= 25 else "🟢"
            st.markdown(f"""
<div class="bar-row">
  <div class="bar-label" title="{dim_val}">{flag} {dim_val}</div>
  <div class="bar-track">
    <div class="{fill}" style="width:{pct_r}%;"></div>
  </div>
  <div class="bar-pct" style="color:{color};">{pct_r}%</div>
  <div style="font-size:11px;color:#9ca3af;width:100px;text-align:right;">{counts['high_risk']}/{total} flagged</div>
</div>""", unsafe_allow_html=True)

    # ── Highest At-Risk Groups ────────────────────────────────────────────────
    st.markdown(f'<div class="sec-head" style="margin-top:28px;">🚨 Highest At-Risk Groups</div>', unsafe_allow_html=True)
    high_risk_sorted = sorted(risk_agg.items(), key=lambda x: x[1]["high_risk"]/max(x[1]["total"],1), reverse=True)[:3]
    hr_cols = st.columns(len(high_risk_sorted)) if high_risk_sorted else []
    for col, (dim_val, counts) in zip(hr_cols, high_risk_sorted):
        total = counts["total"] or 1
        pct_r = round(counts["high_risk"]/total*100)
        with col:
            st.markdown(f"""
<div class="kpi-card" style="text-align:center;border-color:#fca5a5;">
  <div style="font-size:20px;margin-bottom:4px;">🚨</div>
  <div style="font-size:13px;font-weight:700;color:#111;margin-bottom:4px;">{dim_val}</div>
  <div style="font-size:26px;font-weight:700;color:#dc2626;">{pct_r}%</div>
  <div class="kpi-sub">{counts['high_risk']} of {total} flagged at risk</div>
</div>""", unsafe_allow_html=True)

    st.markdown("""
<div style="margin-top:28px;padding:14px 18px;background:#fef9c3;border:1px solid #fcd34d;
            border-radius:10px;font-size:12px;color:#78350f;">
  <strong>⚠️ Note:</strong> Delinquency risk flags are based on prior funding history as a proxy indicator.
  For precise risk scores, use the <strong>Delinquency Risk Assessment</strong> tab with the full logistic regression model.
</div>""", unsafe_allow_html=True)

    # ── Province Choropleth (only when dimension == Province) ─────────────────
    if dimension == "Province":
        st.markdown('<div class="sec-head" style="margin-top:32px;">🗺️ Province Maps — Region VI</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:12px;color:#6b7280;margin-bottom:14px;">Color intensity shows accomplishment rate (left) and at-risk proportion (right) per province.</div>', unsafe_allow_html=True)
        pi_c1, pi_c2 = st.columns(2)
        with pi_c1:
            st.plotly_chart(
                build_choropleth("accomplishment", "IA Accomplishment Rate"),
                use_container_width=True, config={"displayModeBar": False}
            )
        with pi_c2:
            st.plotly_chart(
                build_choropleth("risk", "At-Risk Applicant Rate"),
                use_container_width=True, config={"displayModeBar": False}
            )
    else:
        st.markdown('<div style="margin-top:12px;padding:12px 16px;background:#f0f9ff;border:1px solid #bae6fd;border-radius:10px;font-size:12px;color:#0c4a6e;">💡 Switch the <strong>Analyze by</strong> selector to <strong>Province</strong> to view the geographic choropleth maps.</div>', unsafe_allow_html=True)


st.markdown('</div>', unsafe_allow_html=True)  # close .content
st.markdown("<br><p style='font-size:11px;color:#ccc;text-align:center;'>DOST-VI SETUP 4.0 iFund Program · Region VI</p>", unsafe_allow_html=True)
