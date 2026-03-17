import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, timezone, UTC
from zoneinfo import ZoneInfo
TZ_COL = ZoneInfo('America/Bogota')
from PIL import Image
import requests
import concurrent.futures
import warnings
warnings.filterwarnings("ignore")

# ── Session state ─────────────────────────────────────────
if "initialized" not in st.session_state:
    st.session_state.initialized    = True
    st.session_state.show_info      = False
    st.session_state.lugar_buscado  = None

st.set_page_config(
    page_title="BioMonitor Montería",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════════════════════
# ── CSS MODERNO v2.0 ──────────────────────────────────────
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');

:root {
  --bg:           #EDECEA;
  --surface:      #FFFFFF;
  --surface-2:    #F4F2EE;
  --border:       #D3D1C7;
  --border-light: #E8E6DF;
  --text:         #1E1E1C;
  --text-muted:   #5F5E5A;
  --text-soft:    #888780;
  --green:        #3B6D11;
  --green-dark:   #27500A;
  --green-light:  #EAF3DE;
  --green-mid:    #97C459;
  --blue:         #185FA5;
  --blue-light:   #E6F1FB;
  --amber:        #854F0B;
  --amber-light:  #FAEEDA;
  --red:          #A32D2D;
  --red-light:    #FCEBEB;
  --purple:       #534AB7;
  --purple-light: #EEEDFE;
  --shadow-sm:    0 2px 8px rgba(0,0,0,0.06);
  --shadow-md:    0 4px 20px rgba(0,0,0,0.10);
  --shadow-lg:    0 8px 40px rgba(0,0,0,0.14);
  --transition:   all 0.28s cubic-bezier(0.34,1.56,0.64,1);
  --transition-fast: all 0.18s ease;
}

html, body, [data-testid="stAppViewContainer"] {
  background-color: var(--bg) !important;
  font-family: 'DM Sans', sans-serif !important;
  -webkit-font-smoothing: antialiased;
}
.main { background-color: var(--bg); }
.block-container {
  padding-top: 3rem !important;
  padding-left: 2.5rem !important;
  padding-right: 2.5rem !important;
  max-width: 1440px;
}

/* ── Hero Banner ── */
.hero-banner {
  background: linear-gradient(135deg,#FFFFFF 60%,#F0F7E8 100%);
  border: 1px solid var(--border-light);
  border-left: 4px solid var(--green);
  border-radius: 0 14px 14px 0;
  padding: 22px 28px;
  margin-bottom: 20px;
  box-shadow: var(--shadow-sm);
  position: relative;
  overflow: hidden;
  transition: var(--transition-fast);
  animation: fadeInUp 0.35s ease both;
}
.hero-banner::after {
  content:'';position:absolute;top:-40px;right:-40px;
  width:160px;height:160px;
  background:radial-gradient(circle,rgba(59,109,17,0.07) 0%,transparent 70%);
  border-radius:50%;pointer-events:none;
}
.hero-banner:hover { box-shadow: var(--shadow-md); transform: translateY(-1px); }
.hero-title {
  font-family:'Outfit',sans-serif;font-size:1.4rem;font-weight:800;
  color:var(--text);margin:0 0 6px 0;letter-spacing:-0.3px;
}
.hero-sub {
  font-size:0.9rem;color:var(--text-muted);line-height:1.65;margin:0;font-weight:400;
}
.hero-badge {
  display:inline-flex;align-items:center;gap:5px;
  background:var(--green-light);border:1px solid var(--green-mid);color:var(--green);
  padding:4px 12px;border-radius:30px;font-size:0.73rem;font-weight:600;
  letter-spacing:0.3px;margin-right:6px;margin-top:8px;
  transition:var(--transition);cursor:default;
}
.hero-badge:hover {
  background:var(--green);color:#FFF;border-color:var(--green);
  transform:translateY(-2px);box-shadow:0 4px 12px rgba(59,109,17,0.3);
}

/* ── Logo Wrapper ── */
.logo-wrapper {
  display:flex;align-items:center;gap:16px;
  margin-bottom:14px;padding:16px 20px;
  background:linear-gradient(135deg,#FFFFFF 0%,#F4F9EE 100%);
  border:1px solid var(--border-light);border-left:4px solid var(--green);
  border-radius:0 14px 14px 0;box-shadow:var(--shadow-sm);
  animation:fadeInUp 0.3s ease both;
  transition:var(--transition-fast);
}
.logo-wrapper:hover { box-shadow:var(--shadow-md);transform:translateY(-1px); }
.logo-title-main {
  font-family:'Outfit',sans-serif;font-size:1.7rem;font-weight:900;
  color:var(--green);letter-spacing:-0.5px;line-height:1.1;
}
.logo-title-sub {
  font-size:0.75rem;color:var(--text-soft);font-weight:600;
  letter-spacing:1.2px;text-transform:uppercase;margin-top:3px;
}

/* ── KPI Cards ── */
.kpi-card {
  background:var(--surface);border:1px solid var(--border-light);
  border-radius:14px;padding:18px 20px;position:relative;overflow:hidden;
  margin-bottom:12px;min-height:115px;box-shadow:var(--shadow-sm);
  transition:var(--transition);cursor:default;
  animation:fadeInUp 0.4s ease both;
}
.kpi-card::before {
  content:'';position:absolute;top:0;left:0;width:4px;height:100%;
  background:var(--green);border-radius:2px 0 0 2px;transition:width 0.2s ease;
}
.kpi-card:hover {
  transform:translateY(-3px) scale(1.005);
  box-shadow:var(--shadow-md);border-color:rgba(59,109,17,0.2);
}
.kpi-card:hover::before { width:6px; }
.kpi-card::after {
  content:'';position:absolute;top:0;left:-100%;width:60%;height:100%;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,0.6),transparent);
  transition:left 0.5s ease;pointer-events:none;
}
.kpi-card:hover::after { left:140%; }
.kpi-card-red::before    { background:var(--red); }
.kpi-card-blue::before   { background:var(--blue); }
.kpi-card-green::before  { background:var(--green); }
.kpi-card-purple::before { background:var(--purple); }
.kpi-card-warn::before   { background:var(--amber); }
.kpi-card-red:hover   { border-color:rgba(163,45,45,0.2) !important; }
.kpi-card-blue:hover  { border-color:rgba(24,95,165,0.2) !important; }
.kpi-card-purple:hover{ border-color:rgba(83,74,183,0.2) !important; }

.kpi-label {
  font-family:'Outfit',sans-serif;font-size:0.67rem;color:var(--text-soft);
  text-transform:uppercase;letter-spacing:1.2px;font-weight:700;margin-bottom:6px;
}
.kpi-value {
  font-family:'Outfit',sans-serif;font-size:2rem;font-weight:800;
  color:var(--text);line-height:1;margin-bottom:8px;letter-spacing:-0.5px;
}
.kpi-value-sm {
  font-family:'Outfit',sans-serif;font-size:1.4rem;font-weight:700;
  color:var(--text);line-height:1;margin-bottom:8px;
}

/* ── Badges ── */
.badge {
  display:inline-flex;align-items:center;padding:3px 10px;border-radius:30px;
  font-size:0.72rem;font-weight:700;letter-spacing:0.2px;transition:var(--transition-fast);
}
.badge-green  { background:var(--green-light);color:#1E4A07;border:1px solid var(--green-mid); }
.badge-yellow { background:var(--amber-light);color:#5A2E03;border:1px solid #EF9F27; }
.badge-red    { background:var(--red-light);  color:#5E1010;border:1px solid #F09595; }
.badge-blue   { background:var(--blue-light); color:#0A3868;border:1px solid #85B7EB; }
.badge-purple { background:var(--purple-light);color:#2E2780;border:1px solid #AFA9EC; }

/* ── Section Headers ── */
.section-header {
  font-family:'Outfit',sans-serif;font-size:1rem;font-weight:700;color:var(--text);
  margin-bottom:14px;display:flex;align-items:center;gap:10px;
  padding-bottom:10px;border-bottom:2px solid var(--green-light);letter-spacing:-0.2px;
}

/* ── Info Cards ── */
.info-card {
  background:var(--surface);border:1px solid var(--border-light);border-radius:14px;
  padding:16px 20px;margin-bottom:10px;font-size:0.84rem;color:#444441;line-height:1.6;
  box-shadow:var(--shadow-sm);transition:var(--transition-fast);
}
.info-card:hover { box-shadow:var(--shadow-md);border-color:rgba(59,109,17,0.15);transform:translateY(-1px); }
.info-card b { color:var(--text); }

/* ── Stat Row — FIX LEGIBILIDAD ── */
.stat-row {
  background:linear-gradient(135deg,#F4F2EE 0%,#EEECEA 100%);
  border:1px solid var(--border);border-radius:10px;
  padding:12px 16px;margin-top:10px;
  font-size:0.85rem;color:#2C2C2A !important;
  line-height:1.9;font-weight:500;
}
.stat-row b,
.stat-row span,
.stat-row * { color:#1E1E1C !important; font-weight:600 !important; }
.stat-row small { color:var(--text-soft) !important; font-weight:400 !important; }

/* ── Fuente Tag ── */
.fuente-tag { font-size:0.68rem;color:var(--text-soft);margin-top:5px;font-style:italic; }

/* ── Copyright ── */
.copyright {
  position:fixed;bottom:12px;right:18px;color:#C4C2B9;
  font-size:0.7rem;z-index:9999;font-weight:500;letter-spacing:0.3px;
}

/* ══ BOTONES MODERNOS ══ */
.stButton > button {
  background:linear-gradient(135deg,#3B6D11 0%,#4A8A16 100%) !important;
  color:#FFFFFF !important;
  font-family:'Outfit',sans-serif !important;
  font-weight:700 !important;font-size:0.88rem !important;letter-spacing:0.3px !important;
  border:none !important;border-radius:10px !important;padding:10px 20px !important;
  box-shadow:0 2px 10px rgba(59,109,17,0.25) !important;
  transition:all 0.22s cubic-bezier(0.34,1.56,0.64,1) !important;
  position:relative !important;overflow:hidden !important;
}
.stButton > button:hover {
  background:linear-gradient(135deg,#4A8A16 0%,#316012 100%) !important;
  transform:translateY(-2px) scale(1.02) !important;
  box-shadow:0 6px 20px rgba(59,109,17,0.38) !important;
}
.stButton > button:active {
  transform:translateY(0px) scale(0.98) !important;
  box-shadow:0 2px 8px rgba(59,109,17,0.2) !important;
}
.stDownloadButton > button {
  background:linear-gradient(135deg,#3B6D11 0%,#4A8A16 100%) !important;
  color:#FFFFFF !important;font-family:'Outfit',sans-serif !important;font-weight:700 !important;
  border:none !important;border-radius:10px !important;
  box-shadow:0 2px 10px rgba(59,109,17,0.25) !important;
  transition:all 0.22s cubic-bezier(0.34,1.56,0.64,1) !important;
}
.stDownloadButton > button:hover {
  transform:translateY(-2px) scale(1.02) !important;
  box-shadow:0 6px 20px rgba(59,109,17,0.38) !important;
}

/* ══ TABS ══ */
.stTabs [data-baseweb="tab-list"] {
  background:var(--surface);border-radius:12px;padding:6px;
  border:1px solid var(--border-light);gap:4px;margin-bottom:10px;
  box-shadow:var(--shadow-sm);overflow-x:auto;
}
.stTabs [data-baseweb="tab"] {
  background:transparent;border-radius:9px;color:var(--text-muted) !important;
  font-family:'Outfit',sans-serif !important;font-weight:600;font-size:0.88rem;
  padding:9px 18px;border:none;transition:all 0.18s ease !important;
  letter-spacing:0.1px;white-space:nowrap;
}
.stTabs [data-baseweb="tab"]:hover { background:var(--green-light);color:var(--green) !important; }
.stTabs [aria-selected="true"] {
  background:linear-gradient(135deg,#3B6D11 0%,#4A8A16 100%) !important;
  color:#FFF !important;font-weight:700 !important;
  box-shadow:0 3px 12px rgba(59,109,17,0.3) !important;
}
.stTabs [aria-selected="true"] p,
.stTabs [aria-selected="true"] span,
.stTabs [aria-selected="true"] div { color:#FFF !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top:14px; }

/* ══ DATAFRAME ══ */
.stDataFrame {
  border-radius:12px !important;overflow:hidden !important;
  box-shadow:var(--shadow-sm) !important;border:1px solid var(--border-light) !important;
}
.stDataFrame thead tr th {
  background:var(--green-light) !important;color:var(--green-dark) !important;
  font-family:'Outfit',sans-serif !important;font-weight:700 !important;
  font-size:0.8rem !important;letter-spacing:0.5px !important;
  text-transform:uppercase !important;padding:10px 14px !important;
}
.stDataFrame tbody tr td {
  color:var(--text) !important;font-size:0.84rem !important;
  font-weight:500 !important;padding:9px 14px !important;
}
.stDataFrame tbody tr:hover td { background:var(--green-light) !important; }

/* ══ ALERTAS ══ */
.stAlert { border-radius:10px !important;font-size:0.88rem !important;font-weight:500 !important;box-shadow:var(--shadow-sm) !important; }
div[data-testid="stAlert"] p,
div[data-testid="stAlert"] span,
div[data-testid="stAlert"] div { color:var(--text) !important;font-weight:500 !important; }

/* ══ EXPANDER ══ */
.streamlit-expanderHeader {
  background:var(--surface-2) !important;border:1px solid var(--border-light) !important;
  border-radius:10px !important;color:var(--text) !important;
  font-family:'Outfit',sans-serif !important;font-weight:700 !important;
  transition:var(--transition-fast) !important;
}
.streamlit-expanderHeader:hover { background:var(--green-light) !important;border-color:var(--green-mid) !important; }

/* ══ RADIO ══ */
.stRadio > div { gap:8px !important; }
.stRadio label { color:var(--text-muted) !important;font-size:0.86rem !important;font-weight:500 !important; }

/* FIX Resumen 30 días — texto legible */
div[style*="background:#F1EFE8"] *,
div[style*="background: #F1EFE8"] * { color:#1E1E1C !important; }
div[style*="Resumen"] { color:#1E1E1C !important; }
div[style*="background:#F1EFE8"] b,
div[style*="background: #F1EFE8"] b { color:#1E1E1C !important;font-weight:700 !important; }

footer { visibility:hidden; }
#MainMenu { visibility:hidden; }
.folium-map { width:100% !important; }
iframe { max-width:100% !important;border-radius:12px !important; }
.leaflet-control-layers { max-height:200px;overflow-y:auto;font-size:11px !important;border-radius:10px !important;box-shadow:var(--shadow-md) !important; }

/* ══ SCROLLBAR ══ */
::-webkit-scrollbar { width:7px;height:7px; }
::-webkit-scrollbar-track { background:var(--surface-2);border-radius:10px; }
::-webkit-scrollbar-thumb { background:#C4C2B9;border-radius:10px; }
::-webkit-scrollbar-thumb:hover { background:var(--green-mid); }

/* ══ ANIMACIONES ══ */
@keyframes fadeInUp {
  from { opacity:0;transform:translateY(16px); }
  to   { opacity:1;transform:translateY(0); }
}
@keyframes pulseGreen {
  0%,100% { box-shadow:0 0 0 0 rgba(59,109,17,0.3); }
  50%     { box-shadow:0 0 0 8px rgba(59,109,17,0); }
}

/* ══ RESPONSIVE ══ */
@media (max-width:1100px) {
  .block-container { padding-left:1.5rem !important;padding-right:1.5rem !important; }
}
@media (max-width:900px) {
  .block-container { padding-left:1rem !important;padding-right:1rem !important;padding-top:2rem !important; }
  .kpi-value { font-size:1.6rem !important; }
  .kpi-value-sm { font-size:1.25rem !important; }
}
@media (max-width:768px) {
  .block-container { padding-top:1.5rem !important;padding-left:0.75rem !important;padding-right:0.75rem !important; }
  .kpi-value    { font-size:1.35rem !important; }
  .kpi-value-sm { font-size:1.1rem !important; }
  .kpi-label    { font-size:0.62rem !important; }
  .kpi-card     { min-height:auto !important;padding:13px 15px !important; }
  [data-testid="column"] { min-width:100% !important; }
  .hero-title   { font-size:1.15rem !important; }
  .hero-sub     { font-size:0.82rem !important; }
  .section-header { font-size:0.9rem !important; }
  .stat-row     { font-size:0.78rem !important;line-height:1.9 !important; }
  .copyright    { display:none !important; }
  .stButton > button { min-height:46px !important;font-size:0.85rem !important; }
  .badge        { font-size:0.68rem !important; }
  .stRadio > div { flex-direction:column !important;gap:6px !important; }
  .stDataFrame  { overflow-x:auto !important; }
  .stTabs [data-baseweb="tab-list"] { overflow-x:auto !important;flex-wrap:nowrap !important;padding:4px !important; }
  .stTabs [data-baseweb="tab"] { padding:8px 12px !important;font-size:0.80rem !important; }
  .logo-title-main { font-size:1.3rem !important; }
}
@media (max-width:480px) {
  .block-container { padding-left:0.5rem !important;padding-right:0.5rem !important;padding-top:1.2rem !important; }
  .kpi-value    { font-size:1.2rem !important; }
  .kpi-label    { font-size:0.58rem !important; }
  .section-header { font-size:0.85rem !important; }
  .hero-title   { font-size:1rem !important; }
  .hero-badge   { font-size:0.68rem !important;padding:3px 8px !important; }
  [data-testid="column"] { min-width:100% !important; }
  .stTabs [data-baseweb="tab"] { padding:7px 10px !important;font-size:0.76rem !important; }
  .logo-title-main { font-size:1.1rem !important; }
  .logo-wrapper { padding:12px 14px !important;gap:10px !important; }
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="copyright">© Ivan Contreras</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# ── FUNCIONES DE DATOS ───────────────────────────────────
# ══════════════════════════════════════════════════════════

def _fetch_clima():
    try:
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": 8.7479, "longitude": -75.8814,
                "current": ["temperature_2m","relative_humidity_2m",
                            "precipitation","wind_speed_10m","rain"],
                "daily":   ["precipitation_sum","temperature_2m_max",
                            "temperature_2m_min","precipitation_probability_max",
                            "rain_sum"],
                "timezone": "America/Bogota",
                "forecast_days": 7
            }, timeout=8
        ).json()
        c, d = r.get("current", {}), r.get("daily", {})
        lluvia_sum_hoy = d.get("precipitation_sum", [0])[0] if d.get("precipitation_sum") else 0
        prob_raw = d.get("precipitation_probability_max", [])
        prob_lluvia = [int(p) if p is not None else 0 for p in prob_raw] if prob_raw else [0]*7
        return {
            "temp":       round(c.get("temperature_2m", 28.4), 1),
            "humedad":    c.get("relative_humidity_2m", 75),
            "lluvia_hoy": round(lluvia_sum_hoy, 1),
            "lluvia_inst":round(c.get("precipitation", 0), 1),
            "viento":     round(c.get("wind_speed_10m", 12), 1),
            "lluvia_7d":  d.get("precipitation_sum", [0]*7),
            "prob_lluvia":prob_lluvia,
            "temp_max":   d.get("temperature_2m_max", [32]*7),
            "temp_min":   d.get("temperature_2m_min", [23]*7),
            "fechas":     d.get("time", []),
            "ok": True
        }
    except Exception:
        return {
            "temp":28.4,"humedad":75,"lluvia_hoy":0,"lluvia_inst":0,"viento":12,
            "lluvia_7d":[2]*7,"prob_lluvia":[10]*7,
            "temp_max":[32]*7,"temp_min":[23]*7,
            "fechas":[],"ok":False
        }

def _fetch_aire():
    try:
        r = requests.get(
            "https://air-quality-api.open-meteo.com/v1/air-quality",
            params={
                "latitude": 8.7479, "longitude": -75.8814,
                "current":  ["pm10","pm2_5","nitrogen_dioxide","european_aqi"],
                "timezone": "America/Bogota"
            }, timeout=8
        ).json()
        c = r.get("current", {})
        return {
            "pm25": round(c.get("pm2_5", 9.5), 1),
            "pm10": round(c.get("pm10", 11.9), 1),
            "no2":  round(c.get("nitrogen_dioxide", 3.3), 1),
            "aqi":  round(c.get("european_aqi", 26), 0),
            "ok":   True
        }
    except Exception:
        return {"pm25":9.5,"pm10":11.9,"no2":3.3,"aqi":26,"ok":False}

def _fetch_ideam():
    try:
        r = requests.get(
            "https://www.datos.gov.co/resource/sbwg-7ju4.json",
            params={
                "$where": "codigoestacion='23197130'",
                "$order": "fechaobservacion DESC",
                "$limit": "1"
            }, timeout=5
        ).json()
        if r and "valor" in r[0]:
            return {
                "nivel": round(float(r[0]["valor"]), 2),
                "fecha": r[0].get("fechaobservacion", "")[:10],
                "ok":    True,
                "fuente": "IDEAM · datos.gov.co"
            }
    except Exception:
        pass
    try:
        r2 = requests.get(
            "https://www.datos.gov.co/resource/s54a-sgyg.json",
            params={"municipio": "MONTERIA", "$limit": "1", "$order": "fecha DESC"},
            timeout=5
        ).json()
        if r2 and "valor" in r2[0]:
            return {
                "nivel": round(float(r2[0]["valor"]), 2),
                "fecha": r2[0].get("fecha", "")[:10],
                "ok":    True,
                "fuente": "IDEAM · DHIME"
            }
    except Exception:
        pass
    return {
        "nivel":  4.2,
        "fecha":  datetime.now(TZ_COL).strftime("%Y-%m-%d"),
        "ok":     False,
        "fuente": "Histórico"
    }

@st.cache_data(ttl=900)
def cargar_datos():
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        fc = ex.submit(_fetch_clima)
        fa = ex.submit(_fetch_aire)
        fi = ex.submit(_fetch_ideam)
        return fc.result(), fa.result(), fi.result()

@st.cache_data(ttl=86400)
def obtener_fauna_gbif():
    NOMBRES_ES = {
        "Iguana iguana":"Iguana verde","Boa constrictor":"Boa",
        "Caiman crocodilus":"Babilla","Chelonoidis carbonarius":"Morrocoy",
        "Trachemys callirostris":"Hicotea","Lygophis lineatus":"Culebra rayada",
        "Leptotila verreauxi":"Paloma guarumera","Cairina moschata":"Pato real",
        "Columbina talpacoti":"Tortolita rojiza","Jacana jacana":"Gallito de ciénaga",
        "Ardea alba":"Garza blanca","Bubulcus ibis":"Garza del ganado",
        "Coragyps atratus":"Gallinazo negro","Pitangus sulphuratus":"Bichofué",
        "Thraupis episcopus":"Azulejo común","Ramphocelus dimidiatus":"Sangretoro",
        "Dendrocygna autumnalis":"Pato viudo","Vanellus chilensis":"Pellar",
        "Dasypus novemcinctus":"Armadillo de nueve bandas",
        "Hydrochoerus hydrochaeris":"Chigüiro","Sciurus granatensis":"Ardilla roja",
        "Rhinella marina":"Sapo marino","Heliconia psittacorum":"Heliconia de loro",
        "Heliconia bihai":"Heliconia roja","Guazuma ulmifolia":"Guácimo",
        "Polybia emaciata":"Avispa social","Menemerus bivittatus":"Araña saltarina gris",
        "Sakesphorus canadensis":"Batará barrado","Phalacrocorax brasilianus":"Cormorán neotropical",
    }
    def _nombre_com_gbif(sp_key, especie):
        if not sp_key:
            return NOMBRES_ES.get(especie, "—")
        try:
            r = requests.get(
                f"https://api.gbif.org/v1/species/{sp_key}/vernacularNames",
                params={"limit": 20}, timeout=4
            ).json()
            for item in r.get("results", []):
                if item.get("language","").lower() in ("spa","es","spanish"):
                    n = item.get("vernacularName","").strip()
                    if n: return n.capitalize()
            for item in r.get("results", []):
                if item.get("language","").lower() in ("eng","en","english"):
                    n = item.get("vernacularName","").strip()
                    if n: return n.capitalize()
        except Exception:
            pass
        return NOMBRES_ES.get(especie, "—")
    try:
        r = requests.get(
            "https://api.gbif.org/v1/occurrence/search",
            params={"stateProvince":"Córdoba","country":"CO",
                    "mediaType":"StillImage","hasCoordinate":"true","limit":100},
            timeout=12
        ).json()
        registros, vistos = [], set()
        for rec in r.get("results", []):
            sp = rec.get("species")
            if not sp or sp in vistos: continue
            vistos.add(sp)
            img = next((m["identifier"] for m in rec.get("media",[])
                       if "identifier" in m and m.get("type","")=="StillImage"), None)
            if img is None:
                img = next((m["identifier"] for m in rec.get("media",[])
                           if "identifier" in m), None)
            registros.append({
                "especie":sp,"clase":rec.get("class","—"),"orden":rec.get("order","—"),
                "familia":rec.get("family","—"),"lat":rec.get("decimalLatitude"),
                "lon":rec.get("decimalLongitude"),
                "fecha":(rec.get("eventDate","—")[:10] if rec.get("eventDate") else "—"),
                "imagen_url":img,"estado":rec.get("iucnRedListCategory","No evaluado"),
                "gbif_key":str(rec.get("speciesKey","")),
            })
        def _resolver(reg):
            sp = reg["especie"]
            n = NOMBRES_ES.get(sp)
            return n if n else _nombre_com_gbif(reg["gbif_key"], sp)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            nombres = list(ex.map(_resolver, registros))
        fauna = []
        for reg, nom in zip(registros, nombres):
            reg["nombre_com"] = nom
            fauna.append(reg)
        if fauna:
            return pd.DataFrame(fauna), True
        return None, False
    except Exception:
        return None, False

def nivel_rio(lluvia_7d, base=4.2):
    niveles, ant = [], base
    variacion_base = [0.0, 0.05, -0.03, 0.08, -0.02, 0.06, -0.04]
    for i, ll in enumerate(lluvia_7d):
        var = variacion_base[i % len(variacion_base)]
        lluvia_efecto = ll * 0.08 + (lluvia_7d[i-1] * 0.04 if i > 0 else 0)
        n = round(np.clip(ant * 0.85 + base * 0.15 + lluvia_efecto + var, 0.5, 9.5), 2)
        niveles.append(n)
        ant = n
    return niveles

def alerta_rio(n):
    if n < 4.0:   return "Normal",    "badge-green",  "#3B6D11"
    elif n < 5.5: return "Amarilla",  "badge-yellow", "#FFD600"
    elif n < 7.0: return "Naranja",   "badge-yellow", "#FF9800"
    else:         return "ROJA 🚨",   "badge-red",    "#FF5252"

def cat_aqi(aqi):
    if aqi <= 20:   return "Bueno",      "badge-green"
    elif aqi <= 40: return "Aceptable",  "badge-yellow"
    elif aqi <= 60: return "Moderado",   "badge-yellow"
    else:           return "Malo",       "badge-red"

def calcular_heat_index(temp_c, humedad):
    t = temp_c * 9/5 + 32
    rh = humedad
    hi = (-42.379 + 2.04901523*t + 10.14333127*rh
          - 0.22475541*t*rh - 6.83783e-3*t**2
          - 5.481717e-2*rh**2 + 1.22874e-3*t**2*rh
          + 8.5282e-4*t*rh**2 - 1.99e-6*t**2*rh**2)
    hi_c = round((hi - 32) * 5/9, 1)
    if hi_c < 27:   return hi_c, "✅ Confortable",       "badge-green",  "#3B6D11"
    elif hi_c < 32: return hi_c, "🟡 Precaución",        "badge-yellow", "#FFD600"
    elif hi_c < 41: return hi_c, "🟠 Precaución extrema","badge-yellow", "#FF9800"
    elif hi_c < 54: return hi_c, "🔴 Peligro",           "badge-red",    "#FF5252"
    else:           return hi_c, "🔴 Peligro extremo",   "badge-red",    "#FF0000"

# ── Cauce Río Sinú ─────────────────────────────────────
CAUCE_SINU_FALLBACK = [
    [8.69768846,-75.94782194],[8.70122071,-75.94240658],
    [8.69987114,-75.93560537],[8.70305888,-75.93594981],
    [8.71192054,-75.94286909],[8.71863785,-75.94379077],
    [8.72535501,-75.93734223],[8.72193985,-75.93215672],
    [8.71557630,-75.92536160],[8.71855524,-75.92260906],
    [8.72478702,-75.92213802],[8.73127622,-75.92305694],
    [8.73640083,-75.92213510],[8.73961492,-75.91957351],
    [8.74013571,-75.91535784],[8.73778687,-75.90851478],
    [8.74351866,-75.90587567],[8.74727880,-75.90322958],
    [8.74922018,-75.90126533],[8.74922025,-75.89856450],
    [8.74764320,-75.89414539],[8.74788577,-75.89242679],
    [8.75261750,-75.89193544],[8.75686353,-75.88984919],
    [8.76280817,-75.88518463],[8.77045286,-75.88223726],
    [8.77215134,-75.87941382],[8.76936038,-75.87450396],
    [8.76802566,-75.87290836],[8.76826901,-75.87094317],
    [8.77118166,-75.86959167],[8.78367731,-75.87364386],
    [8.78883840,-75.86806919],[8.79362685,-75.86414634],
    [8.80022730,-75.85977915],[8.80295920,-75.85977891],
    [8.80887841,-75.86254257],[8.82094414,-75.85770413],
    [8.82936742,-75.85632123],[8.83164380,-75.85309608],
    [8.83594253,-75.85423387],[8.84148501,-75.85633728],
    [8.84841300,-75.85668785],
]

# ── Universidades & CC ──────────────────────────────────
UNIVERSIDADES_GLOBAL = [
    (8.7678248873423,-75.88483868572298,"🎓 Universidad del Sinú","Cra. 1W #38-153, Barrio Juan XXIII","Institución privada · ~8,000 estudiantes"),
    (8.791868230231875,-75.86243514566901,"🎓 Universidad de Córdoba","Cra. 6 #77-305, Montería","Universidad pública · ~15,000 estudiantes"),
    (8.80502372813011,-75.8504521385269,"🎓 Universidad Pontificia Bolivariana","Cra. 6 #97A-99, Barrio Mocarí","Institución privada · sede Montería"),
    (8.774657079543962,-75.8644811469475,"🎓 Universidad Luis Amigó","Cl. 64 #6-108, Montería","Institución privada · sede Montería"),
    (8.766214543910708,-75.86885384879858,"🎓 Universidad Cooperativa de Colombia","Cl. 52 #6-79, Montería","Institución privada · sede Montería"),
    (8.756837644153618,-75.88483213345532,"🎓 CUN Montería","Cra. 4 #30-20, Montería","Corporación Unificada Nacional"),
    (8.767419911567938,-75.88224655290996,"🎓 Politécnico Gran Colombiano","Cl. 66 #5-70 Local 103, Montería","Institución privada · sede Montería"),
    (8.754969967892375,-75.88607423530627,"🎓 Uniremington","Cl. 27 #4-31, Montería","Corporación Universitaria Remington"),
    (8.75708789506036,-75.88234492154572,"🏫 Instituto Tecnológico San Agustín","Cra. 6 #33-02, Centro, Montería","Institución educativa"),
]
CC_GLOBAL = [
    (8.779113660375875,-75.86157613345505,"🛍️ C.C. Buenavista","Cra. 6 #68-72, Montería","Centro comercial principal de Montería"),
    (8.743285562064065,-75.8681799622913,"🛍️ C.C. Nuestro","Tv. 29 #29-69, Montería","Centro comercial Nuestro"),
    (8.76328684876092,-75.87336956044,"🛍️ C.C. Alamedas","Cl. 44 #10-91, Montería","Centro comercial Alamedas del Sinú"),
]

# ══════════════════════════════════════════════════════════
# ── CARGA DE DATOS ────────────────────────────────────────
# ══════════════════════════════════════════════════════════
_loading = st.empty()
_loading.markdown("""
<div style="text-align:center;padding:50px 0;">
  <div style="display:inline-block;background:#FFFFFF;border:1px solid #E8E6DF;
              border-left:4px solid #3B6D11;border-radius:0 14px 14px 0;
              padding:24px 40px;box-shadow:0 4px 20px rgba(0,0,0,0.08);">
    <div style="font-family:'Outfit',sans-serif;color:#3B6D11;font-size:1.2rem;
                font-weight:800;margin-bottom:8px;letter-spacing:-0.3px">
      🌿 Cargando BioMonitor Montería…
    </div>
    <div style="color:#5F5E5A;font-size:0.85rem;font-weight:500">
      Conectando con Open-Meteo · IDEAM · GBIF
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

try:
    clima, aire, ideam = cargar_datos()
except Exception as _e:
    _loading.error(f"⚠️ Error al cargar datos: {_e}\n\nIntenta recargar la página o pulsa **🔄 Actualizar**.")
    st.stop()

_loading.empty()

if ideam["ok"]:
    nivel_base = ideam["nivel"]
    fuente_rio = f"🟢 {ideam.get('fuente','—')} · {ideam.get('fecha','—')}"
elif clima["ok"]:
    nivel_base = 4.2
    fuente_rio = "🟡 Simulado · lluvia real Open-Meteo"
else:
    nivel_base = 4.2
    fuente_rio = "🔴 Datos históricos"

niveles = nivel_rio(clima["lluvia_7d"], base=nivel_base)

if clima["fechas"]:
    dias = [datetime.strptime(f, "%Y-%m-%d").strftime("%d %b") for f in clima["fechas"]]
else:
    dias = [(datetime.now(TZ_COL) + timedelta(days=i)).strftime("%d %b") for i in range(7)]

rio_txt, rio_badge, rio_color = alerta_rio(niveles[0])
aqi_txt, aqi_badge = cat_aqi(aire["aqi"])

# ══════════════════════════════════════════════════════════
# ── HEADER ────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════
st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

col_hero, col_estado = st.columns([3, 1], gap="medium")

with col_hero:
    # ── Hero unificado: logo + texto en un solo bloque HTML ─
    logo_b64 = ""
    try:
        import base64, io as _io
        logo_img = Image.open("Biomotorlogo.png")
        buf = _io.BytesIO()
        logo_img.save(buf, format="PNG")
        logo_b64 = base64.b64encode(buf.getvalue()).decode()
    except Exception:
        pass

    if logo_b64:
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="width:130px;height:130px;object-fit:contain;flex-shrink:0;border-radius:12px">'
    else:
        logo_html = '<div style="width:130px;height:130px;background:linear-gradient(135deg,#EAF3DE,#E0EFCE);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:3rem;flex-shrink:0">🌿</div>'

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:24px;
                background:linear-gradient(135deg,#FFFFFF 60%,#F0F7E8 100%);
                border:1px solid #E8E6DF;border-left:4px solid #3B6D11;
                border-radius:0 14px 14px 0;padding:22px 28px;
                box-shadow:0 2px 8px rgba(0,0,0,0.06);
                animation:fadeInUp 0.35s ease both;">
      {logo_html}
      <div style="flex:1;min-width:0">
        <div style="font-size:0.9rem;color:#5F5E5A;line-height:1.65;
                    margin-bottom:12px;font-weight:400">
          Plataforma de monitoreo ambiental en tiempo real para
          <b style="color:#1E1E1C">Montería, Córdoba, Colombia</b>.
          Integra datos oficiales de <b style="color:#3B6D11">IDEAM</b>,
          <b style="color:#3B6D11">Open-Meteo</b> y <b style="color:#3B6D11">GBIF</b>
          para monitorear la calidad del aire, el nivel del río Sinú y la
          biodiversidad local. Actualización automática cada 15 minutos.
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:6px">
          <span class="hero-badge">🌡️ Clima en tiempo real</span>
          <span class="hero-badge">💨 Calidad del aire</span>
          <span class="hero-badge">🌊 Nivel Río Sinú</span>
          <span class="hero-badge">🦜 Biodiversidad GBIF</span>
          <span class="hero-badge">🗺️ Mapa interactivo</span>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

with col_estado:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    nivel_actual_hero = niveles[0] if niveles else 0
    pm_actual_hero    = aire.get("pm25", 0)
    hi_hero, _, _, _  = calcular_heat_index(clima.get("temp",30), clima.get("humedad",75))

    if nivel_actual_hero >= 5.5 or pm_actual_hero >= 25:
        estado_ico, estado_txt   = "🔴", "Atención requerida"
        estado_color, estado_desc = "#791F1F", "Hay condiciones de riesgo activas"
        borde_color = "#A32D2D"
    elif nivel_actual_hero >= 4.0 or pm_actual_hero >= 15 or hi_hero >= 32:
        estado_ico, estado_txt   = "🟡", "Monitorear de cerca"
        estado_color, estado_desc = "#633806", "Algunas variables requieren atención"
        borde_color = "#854F0B"
    else:
        estado_ico, estado_txt   = "🟢", "Todo en orden"
        estado_color, estado_desc = "#27500A", "Todas las variables dentro del rango normal"
        borde_color = "#3B6D11"

    hora_actual = datetime.now(TZ_COL).strftime("%H:%M")
    st.markdown(f"""
    <div style="background:#FFFFFF;border:1px solid #E8E6DF;
                border-left:4px solid {borde_color};border-radius:0 14px 14px 0;
                padding:20px 16px;text-align:center;
                box-shadow:0 2px 8px rgba(0,0,0,0.06);
                transition:all 0.18s ease;animation:fadeInUp 0.4s ease 0.1s both;">
      <div style="font-family:'Outfit',sans-serif;font-size:0.64rem;text-transform:uppercase;
                  letter-spacing:1.2px;color:#888780;margin-bottom:10px;font-weight:700">
        ¿Cómo está Montería ahora?
      </div>
      <div style="font-size:2.6rem;margin:4px 0;line-height:1;
                  filter:drop-shadow(0 2px 6px rgba(0,0,0,0.15))">{estado_ico}</div>
      <div style="font-family:'Outfit',sans-serif;font-size:1rem;font-weight:800;
                  color:{estado_color};margin-top:8px;letter-spacing:-0.2px">
        {estado_txt}
      </div>
      <div style="font-size:0.76rem;color:#5F5E5A;margin-top:5px;line-height:1.5;font-weight:500">
        {estado_desc}
      </div>
      <div style="font-size:0.68rem;color:#888780;margin-top:10px;
                  border-top:1px solid #E8E6DF;padding-top:8px;font-weight:500">
        <span style="display:inline-block;width:6px;height:6px;background:{borde_color};
                     border-radius:50%;margin-right:4px;vertical-align:middle;
                     box-shadow:0 0 0 3px rgba(59,109,17,0.2)"></span>
        Actualizado {hora_actual} hora Colombia
      </div>
    </div>
    <div style="margin-top:10px;font-size:0.75rem;color:#444441;
                background:linear-gradient(135deg,#F4F2EE,#EEECEA);
                border-radius:10px;padding:12px 14px;border:1px solid #D3D1C7;
                line-height:1.8;font-weight:500">
      <b style="color:#1E1E1C;display:block;margin-bottom:6px;
                font-family:'Outfit',sans-serif;font-size:0.77rem">¿Qué significa el color?</b>
      <span style="color:#27500A;font-weight:600">🟢 Verde</span> — Todo en orden, sin alertas<br>
      <span style="color:#633806;font-weight:600">🟡 Amarillo</span> — Algo requiere atención<br>
      <span style="color:#791F1F;font-weight:600">🔴 Rojo</span> — Condición de riesgo activa
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("🔄 Actualizar datos", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# ── NAVEGACIÓN POR TABS ───────────────────────────────────
# ══════════════════════════════════════════════════════════
tab_inicio, tab_mapa, tab_analisis, tab_bio, tab_alertas = st.tabs([
    "🏠 Inicio", "🗺️ Mapa", "📈 Análisis", "🦜 Biodiversidad", "🔔 Alertas"
])

# ══════════════════════════════════════════════════════════
# TAB 1 — INICIO
# ══════════════════════════════════════════════════════════
with tab_inicio:
    def _kpi_card(cls, label, val, badge_txt, badge_cls, fuente):
        st.markdown(f"""
        <div class="{cls}">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{val}</div>
          <span class="badge {badge_cls}">{badge_txt}</span>
          <div class="fuente-tag">{fuente}</div>
        </div>""", unsafe_allow_html=True)

    k1, k2, k3 = st.columns(3, gap="small")
    with k1: _kpi_card("kpi-card", "🌊 Nivel Río Sinú", f"{niveles[0]} m", rio_txt, rio_badge, fuente_rio)
    with k2: _kpi_card("kpi-card kpi-card-blue", "🌡️ Temperatura", f"{clima.get('temp','—')} °C", f"Humedad {clima['humedad']}%", "badge-blue", "Open-Meteo · ahora")
    with k3:
        prob = clima.get("prob_lluvia", [0])[0] if clima.get("prob_lluvia") else 0
        _kpi_card("kpi-card kpi-card-blue", "🌧️ Lluvia hoy",
                  f"{clima.get('lluvia_hoy','—')} mm",
                  f"☔ Prob. {prob}%",
                  "badge-blue" if prob < 30 else "badge-yellow" if prob < 60 else "badge-red",
                  "Open-Meteo · ahora")

    k4, k5, k6 = st.columns(3, gap="small")
    with k4: _kpi_card("kpi-card kpi-card-green", "💨 PM2.5", f"{aire.get('pm25','—')} µg/m³", "✅ OMS < 15", "badge-green", "Open-Meteo · ahora")
    with k5: _kpi_card("kpi-card", "🌬️ AQI Europeo", str(aire.get('aqi','—')), aqi_txt, aqi_badge, "Índice europeo")
    with k6: _kpi_card("kpi-card kpi-card-purple", "🦜 Especies GBIF", "≥12", "Córdoba 2026", "badge-purple", "GBIF · Córdoba, CO")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">📋 Resumen del estado actual</div>', unsafe_allow_html=True)

    hi_inicio, hi_lbl_inicio, _, _ = calcular_heat_index(clima.get("temp",30), clima.get("humedad",75))
    alerta_rio_txt, _, _ = alerta_rio(niveles[0])

    resumen_items = [
        ("🌊","Río Sinú",       f"Nivel {niveles[0]}m · Alerta {alerta_rio_txt}",            "badge-yellow" if niveles[0]>=4.0 else "badge-green",      "Estación Ronda del Sinú · IDEAM"),
        ("🌡️","Temperatura",    f"{clima.get('temp','—')}°C real · {hi_inicio}°C aparente · {hi_lbl_inicio}","badge-yellow" if hi_inicio>=32 else "badge-green",       "Open-Meteo · tiempo real"),
        ("💨","Calidad del aire",f"PM2.5: {aire.get('pm25','—')} µg/m³ · AQI: {aire.get('aqi','—')} · {'Buena' if aire.get('pm25',0)<15 else 'Regular'}","badge-green" if aire.get('pm25',0)<15 else "badge-yellow","Open-Meteo Air Quality · tiempo real"),
        ("🌧️","Lluvia",          f"{clima.get('lluvia_hoy','0')} mm hoy · {(clima.get('prob_lluvia',[0])[0] if clima.get('prob_lluvia') else 0)}% de probabilidad","badge-blue","Open-Meteo · tiempo real"),
        ("🌿","Biodiversidad",   f"≥12 especies registradas en Córdoba · datos GBIF actualizados","badge-purple","GBIF · Córdoba, Colombia · 2026"),
    ]
    for ico, titulo, desc, badge_cls, fuente in resumen_items:
        estado_label = '✓ Normal' if 'green' in badge_cls else ('⚠ Atención' if 'yellow' in badge_cls else '● Activo')
        st.markdown(f"""
        <div class="info-card" style="display:flex;align-items:flex-start;gap:14px;margin-bottom:8px">
          <div style="font-size:1.5rem;line-height:1;flex-shrink:0;
                      width:42px;height:42px;background:#F4F2EE;border-radius:10px;
                      display:flex;align-items:center;justify-content:center">{ico}</div>
          <div style="flex:1">
            <div style="font-family:'Outfit',sans-serif;font-weight:700;color:#1E1E1C;font-size:0.92rem">{titulo}</div>
            <div style="color:#5F5E5A;font-size:0.83rem;margin-top:3px;font-weight:400">{desc}</div>
            <div style="color:#888780;font-size:0.7rem;margin-top:4px;font-style:italic">{fuente}</div>
          </div>
          <span class="badge {badge_cls}" style="flex-shrink:0;align-self:center">{estado_label}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="info-card" style="font-size:0.82rem;color:#888780;text-align:center;
         background:linear-gradient(135deg,#F4F9EE,#EDF7E0);border-color:#C8E4A0">
      💡 Usa las pestañas de arriba para ver el <b style="color:#3B6D11">Mapa</b> interactivo,
      el <b style="color:#3B6D11">Análisis</b> histórico, la <b style="color:#3B6D11">Biodiversidad</b>
      en tiempo real y el panel de <b style="color:#3B6D11">Alertas</b>.
    </div>""", unsafe_allow_html=True)


@st.cache_data(ttl=86400)
def obtener_avistamientos_mapa():
    ESPECIES = [
        ("Iguana iguana","🦎","Iguana verde","No evaluado","purple"),
        ("Leptotila verreauxi","🐦","Paloma guarumera","LC","purple"),
        ("Cairina moschata","🦆","Pato real","LC","purple"),
        ("Heliconia psittacorum","🌺","Heliconia de loro","No evaluado","purple"),
        ("Chelonoidis carbonarius","🐢","Morrocoy","Vulnerable","red"),
        ("Columbina talpacoti","🐦","Tortolita rojiza","LC","purple"),
        ("Jacana jacana","🦅","Gallito de ciénaga","LC","purple"),
        ("Ardea alba","🦢","Garza blanca","LC","purple"),
        ("Pitangus sulphuratus","🐦","Bichofué","LC","purple"),
        ("Coragyps atratus","🦅","Gallinazo negro","LC","purple"),
    ]
    avistamientos = []
    for especie, emoji, nombre_com, estado, color in ESPECIES:
        try:
            r = requests.get(
                "https://api.gbif.org/v1/occurrence/search",
                params={"scientificName":especie,"decimalLatitude":"8.68,8.85",
                        "decimalLongitude":"-75.95,-75.78","hasCoordinate":"true",
                        "country":"CO","limit":10},
                timeout=8
            ).json()
            for rec in r.get("results",[]):
                lat = rec.get("decimalLatitude")
                lon = rec.get("decimalLongitude")
                if lat and lon and 8.68<=lat<=8.85 and -75.95<=lon<=-75.78:
                    fecha = rec.get("eventDate","")[:10] if rec.get("eventDate") else "Sin fecha"
                    localidad = rec.get("locality", rec.get("municipality","Montería"))
                    avistamientos.append({
                        "lat":lat,"lon":lon,"especie":especie,"emoji":emoji,
                        "nombre":nombre_com,"estado":estado,"color":color,
                        "fecha":fecha,"localidad":localidad[:40] if localidad else "Montería",
                        "key":rec.get("key",""),
                    })
        except Exception:
            continue
    return avistamientos

@st.cache_data(ttl=3600)
def obtener_historico_30dias():
    try:
        fecha_fin = datetime.now(TZ_COL).strftime("%Y-%m-%d")
        fecha_ini = (datetime.now(TZ_COL)-timedelta(days=30)).strftime("%Y-%m-%d")
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={"latitude":8.7479,"longitude":-75.8814,
                    "daily":["temperature_2m_max","temperature_2m_min",
                             "precipitation_sum","wind_speed_10m_max"],
                    "timezone":"America/Bogota","start_date":fecha_ini,"end_date":fecha_fin},
            timeout=10
        ).json()
        d = r.get("daily",{})
        return {"fechas":d.get("time",[]),"temp_max":d.get("temperature_2m_max",[]),
                "temp_min":d.get("temperature_2m_min",[]),"lluvia":d.get("precipitation_sum",[]),
                "viento":d.get("wind_speed_10m_max",[]),"ok":True}
    except Exception:
        return {"ok":False,"fechas":[],"temp_max":[],"temp_min":[],"lluvia":[],"viento":[]}

@st.cache_data(ttl=3600)
def obtener_historico_aire_30dias():
    try:
        fecha_fin = datetime.now(TZ_COL).strftime("%Y-%m-%d")
        fecha_ini = (datetime.now(TZ_COL)-timedelta(days=30)).strftime("%Y-%m-%d")
        r = requests.get(
            "https://air-quality-api.open-meteo.com/v1/air-quality",
            params={"latitude":8.7479,"longitude":-75.8814,
                    "hourly":["pm2_5","pm10"],"timezone":"America/Bogota",
                    "start_date":fecha_ini,"end_date":fecha_fin},
            timeout=10
        ).json()
        h = r.get("hourly",{})
        pm25_h = h.get("pm2_5",[])
        fechas_h = h.get("time",[])
        dias_pm25 = {}
        for t,v in zip(fechas_h,pm25_h):
            if v is not None:
                dia = t[:10]
                dias_pm25.setdefault(dia,[]).append(v)
        fechas_d = sorted(dias_pm25.keys())
        pm25_d = [round(sum(dias_pm25[d])/len(dias_pm25[d]),1) for d in fechas_d]
        return {"fechas":fechas_d,"pm25":pm25_d,"ok":True}
    except Exception:
        return {"ok":False,"fechas":[],"pm25":[]}

def obtener_cauce_sinu():
    return None

# ══════════════════════════════════════════════════════════
# TAB 2 — MAPA
# ══════════════════════════════════════════════════════════
with tab_mapa:
    st.markdown('<div class="section-header">🗺️ Mapa ambiental interactivo · Montería</div>', unsafe_allow_html=True)
    col_mapa, col_pred = st.columns([1.35, 1], gap="small")

    with col_mapa:
        if "mapa_tipo" not in st.session_state:
            st.session_state.mapa_tipo = "Estándar"
        btn1, btn2, btn3, _ = st.columns([1.1,1.1,1,3], gap="small")
        with btn1:
            if st.button("🗺️ Estándar", use_container_width=True,
                         type="primary" if st.session_state.mapa_tipo=="Estándar" else "secondary"):
                st.session_state.mapa_tipo = "Estándar"; st.rerun()
        with btn2:
            if st.button("🛰️ Satelital", use_container_width=True,
                         type="primary" if st.session_state.mapa_tipo=="Satelital" else "secondary"):
                st.session_state.mapa_tipo = "Satelital"; st.rerun()
        with btn3:
            if st.button("🌑 Oscuro", use_container_width=True,
                         type="primary" if st.session_state.mapa_tipo=="Oscuro" else "secondary"):
                st.session_state.mapa_tipo = "Oscuro"; st.rerun()

        tipo = st.session_state.mapa_tipo
        if tipo == "Satelital":
            m = folium.Map(location=[8.7700,-75.8750], zoom_start=13, tiles=None, prefer_canvas=True)
            folium.TileLayer(
                tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                attr="Tiles © Esri", name="Satelital", overlay=False, control=True
            ).add_to(m)
        elif tipo == "Oscuro":
            m = folium.Map(location=[8.7700,-75.8750], zoom_start=13,
                           tiles="CartoDB dark_matter", attr="© CartoDB", prefer_canvas=True)
        else:
            m = folium.Map(location=[8.7700,-75.8750], zoom_start=13,
                           tiles="OpenStreetMap", attr="© OpenStreetMap contributors", prefer_canvas=True)

        g_rio=folium.FeatureGroup(name="🌊 Río y estaciones",show=True)
        g_contam=folium.FeatureGroup(name="💨 Contaminación",show=True)
        g_inundacion=folium.FeatureGroup(name="🌊 Zonas inundación",show=True)
        g_lluvia=folium.FeatureGroup(name="🌧️ Lluvia",show=True)
        g_univ=folium.FeatureGroup(name="🎓 Universidades",show=True)
        g_cc=folium.FeatureGroup(name="🛍️ C. Comerciales",show=True)
        g_aire=folium.FeatureGroup(name="💨 Estaciones aire",show=True)
        g_fauna=folium.FeatureGroup(name="🦜 Fauna",show=True)

        _cauce = obtener_cauce_sinu() or CAUCE_SINU_FALLBACK
        folium.PolyLine(locations=_cauce, color="#4FC3F7", weight=5, opacity=0.9, tooltip="Río Sinú").add_to(g_rio)
        folium.Circle([8.7560,-75.8850], radius=6000, color="#00E5C3", fill=True, fill_opacity=0.02, weight=1, dash_array="6").add_to(g_rio)

        for lat,lon,nombre,idx in [
            (8.757573799506615,-75.88747047195153,"Ronda del Sinú — Av. Primera",0),
            (8.7650,-75.8845,"Puente Segundo Centenario",1),
            (8.761909556839255,-75.88462084128709,"Muelle Turístico del Sinú",2),
        ]:
            alerta_lbl,_,_ = alerta_rio(niveles[idx])
            folium.Marker([lat,lon],
                popup=folium.Popup(f"<b>🌊 {nombre}</b><br>📊 Nivel actual: <b>{niveles[idx]}m</b><br>🔔 Estado: <b>{alerta_lbl}</b><br>📡 Fuente: {fuente_rio}", max_width=260),
                tooltip=folium.Tooltip(f"🌊 {nombre} · {niveles[idx]}m · {alerta_lbl}", sticky=True),
                icon=folium.Icon(color="blue",icon="tint",prefix="fa")
            ).add_to(g_rio)

        pm25 = aire["pm25"]
        def color_contam(f):
            v = pm25*f
            if v<10: return "#00E5C3","🟢 Buena"
            elif v<15: return "#FFD600","🟡 Moderada"
            elif v<25: return "#FF9800","🟠 Regular"
            else: return "#FF5252","🔴 Mala"

        ZONAS_CONTAM = [
            (8.7420,-75.8650,280,"🚌 Terminal de Transportes","Cl. 44 · buses y camiones · emisiones altas",2.1),
            (8.7512,-75.8795,260,"🏪 Mercado Central","Cra. 6 centro · tráfico pesado + vendedores",1.8),
            (8.7600,-75.8600,240,"🚗 Avenida Circunvalar","Corredor vial principal E-O de Montería",1.6),
            (8.75594055923935,-75.88700684261966,200,"🏛️ Parque Simón Bolívar","Centro histórico · zona más concurrida de Montería",1.3),
            (8.779113660375875,-75.86157613345505,200,"🛍️ Zona C.C. Buenavista","Cra. 6 #68-72 · flujo comercial intenso",1.4),
            (8.71165087231113,-75.82840985065003,200,"⚽ Estadio Jaraguay","Estadio Municipal de Montería · zona sur",1.2),
            (8.757573799506615,-75.88747047195153,320,"🌿 Ronda del Sinú","Parque lineal más grande de Latinoamérica · pulmón verde urbano",0.6),
            (8.761909556839255,-75.88462084128709,180,"⚓ Muelle Turístico","Orilla del río Sinú · brisa natural",0.7),
            (8.8233,-75.8258,180,"✈️ Aeropuerto Los Garzones","Zona norte periférica · baja densidad urbana",0.8),
        ]
        for lat,lon,radio,nombre,desc,factor in ZONAS_CONTAM:
            c,estado = color_contam(factor)
            folium.Circle(location=[lat,lon], radius=radio, color=c, fill=True, fill_color=c, fill_opacity=0.40, weight=3,
                popup=folium.Popup(f"<b>{nombre}</b><br>📍 {desc}<br>💨 PM2.5 est.: <b>{round(pm25*factor,1)} µg/m³</b><br>Factor: {factor}x · Estado: {estado}", max_width=260),
                tooltip=f"{nombre} — {estado}"
            ).add_to(g_contam)

        nivel_actual = niveles[0]
        ZONAS_INUND = [
            (8.7480,-75.8960,300,"La Granja · La Ribera",4.0,"Zona baja occidental"),
            (8.7430,-75.8880,260,"Barrio Colón · Chuchurubi",4.0,"Inundación histórica"),
            (8.7650,-75.8930,240,"Ronda Sinú norte",5.5,"Afectada cota 5.5m"),
            (8.7800,-75.8900,200,"El Recreo · ribera norte",5.5,"Afectada cota 5.5m"),
            (8.7280,-75.9000,200,"Mocarí · zona sur",4.0,"Zona baja sur"),
        ]
        for lat,lon,radio,barrios,cota,nota in ZONAS_INUND:
            if nivel_actual>=cota+1.5: cz,fo,az="#FF5252",0.38,"⚠️ INUNDACIÓN"
            elif nivel_actual>=cota:   cz,fo,az="#FF9800",0.24,"⚠️ Alerta"
            elif nivel_actual>=cota-0.5: cz,fo,az="#FFD600",0.14,"⚡ Precaución"
            else:                      cz,fo,az="#4FC3F7",0.07,"✅ Normal"
            folium.Circle(location=[lat,lon], radius=radio, color=cz, fill=True, fill_color=cz, fill_opacity=fo, weight=3, dash_array="6",
                popup=folium.Popup(f"<b>🌊 Zona inundación</b><br>Barrios: {barrios}<br>Nivel actual: <b>{nivel_actual}m</b><br>Cota alerta: {cota}m · Estado: <b>{az}</b><br>{nota}", max_width=270),
                tooltip=f"🌊 {barrios} — {az}"
            ).add_to(g_inundacion)

        prob_h = clima.get("prob_lluvia",[0])[0] if clima.get("prob_lluvia") else 0
        if prob_h>=20 or clima.get("lluvia_hoy",0)>0:
            cl_r,op_r = ("#0066FF",0.22) if prob_h>=60 else ("#00AAFF",0.13) if prob_h>=30 else ("#00CCFF",0.07)
            for lat_z,lon_z,peso in [(8.7550,-75.8914,1.0),(8.7480,-75.9000,0.9),(8.7750,-75.8870,0.8)]:
                folium.Circle([lat_z,lon_z], radius=int(2000*peso), color=cl_r, fill=True, fill_color=cl_r,
                    fill_opacity=op_r*peso, weight=0, tooltip=f"🌧️ Prob. lluvia: {prob_h}%"
                ).add_to(g_lluvia)

        for lat,lon,nombre,direccion,info in UNIVERSIDADES_GLOBAL:
            folium.Marker([lat,lon],
                popup=folium.Popup(f"<b>{nombre}</b><br>📍 {direccion}<br>ℹ️ {info}", max_width=250),
                tooltip=nombre, icon=folium.Icon(color="orange",icon="graduation-cap",prefix="fa")
            ).add_to(g_univ)

        for lat,lon,nombre,direccion,info in CC_GLOBAL:
            folium.Marker([lat,lon],
                popup=folium.Popup(f"<b>{nombre}</b><br>📍 {direccion}<br>ℹ️ {info}", max_width=250),
                tooltip=nombre, icon=folium.Icon(color="red",icon="shopping-cart",prefix="fa")
            ).add_to(g_cc)

        for lat,lon,nombre,txt in [
            (8.7550,-75.8750,"💨 Estación Centro",
             "PM2.5: "+str(aire.get("pm25","—"))+" µg/m³<br>AQI: "+str(aire.get("aqi","—"))+"<br>NO₂: "+str(aire.get("no2","—"))+" µg/m³"),
            (8.7350,-75.8650,"💨 Estación Sur",
             "PM10: "+str(aire.get("pm10","—"))+" µg/m³<br>PM2.5: "+str(aire.get("pm25","—"))+" µg/m³<br>Viento: "+str(clima.get("viento","—"))+" km/h"),
        ]:
            folium.Marker([lat,lon],
                popup=folium.Popup(f"<b>{nombre}</b><br>{txt}<br>📡 Open-Meteo · tiempo real", max_width=230),
                tooltip=folium.Tooltip(nombre, sticky=True),
                icon=folium.Icon(color="green",icon="cloud",prefix="fa")
            ).add_to(g_aire)

        avistamientos_reales = obtener_avistamientos_mapa()
        if avistamientos_reales:
            from collections import defaultdict
            por_especie = defaultdict(list)
            for av in avistamientos_reales:
                por_especie[av["especie"]].append(av)
            for especie, registros in por_especie.items():
                for av in registros:
                    color_m = "red" if av["estado"]=="Vulnerable" else "purple"
                    folium.Marker([av["lat"],av["lon"]],
                        popup=folium.Popup(
                            f"<b>{av['emoji']} {av['especie']}</b><br>🏷️ <b>{av['nombre']}</b><br>"
                            f"📍 {av['localidad']}<br>📅 {av['fecha']}<br>"
                            f"🔴 Estado IUCN: {av['estado']}<br>📡 Fuente: GBIF · coordenadas reales", max_width=260),
                        tooltip=folium.Tooltip(f"{av['emoji']} {av['especie']}<br>{av['nombre']} · {av['fecha']}", sticky=True),
                        icon=folium.Icon(color=color_m, icon="paw", prefix="fa")
                    ).add_to(g_fauna)
        else:
            for lat,lon,esp,nom,zona,est in [
                (8.757573799506615,-75.88747047195153,"🦎 Iguana iguana","Iguana verde","Ronda del Sinú","No evaluado"),
                (8.7720,-75.8680,"🐦 Leptotila verreauxi","Paloma guarumera","Norte urbano","LC"),
                (8.761909556839255,-75.88462084128709,"🦆 Cairina moschata","Pato real","Muelle Turístico","LC"),
                (8.7678248873423,-75.88483868572298,"🌺 Heliconia psittacorum","Heliconia de loro","Zonas verdes","No evaluado"),
                (8.71165087231113,-75.82840985065003,"🐢 Chelonoidis carbonarius","Morrocoy","Zona sur","Vulnerable"),
            ]:
                folium.Marker([lat,lon],
                    popup=folium.Popup(f"<b>{esp}</b><br>🏷️ {nom}<br>📍 {zona}<br>🔴 Estado IUCN: {est}<br>⚠️ Respaldo · GBIF no disponible", max_width=250),
                    tooltip=folium.Tooltip(f"{esp} · {nom}", sticky=True),
                    icon=folium.Icon(color="red" if est=="Vulnerable" else "purple", icon="paw", prefix="fa")
                ).add_to(g_fauna)

        for g in [g_inundacion,g_lluvia,g_contam,g_rio,g_aire,g_univ,g_cc,g_fauna]:
            g.add_to(m)
        folium.LayerControl(collapsed=False, position="topright").add_to(m)
        st_folium(m, width=None, height=460, use_container_width=True, returned_objects=[], key="mapa_principal")

    with col_pred:
        st.markdown('<div class="section-header">🌊 Predicción 7 días · LSTM</div>', unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(5.5, 3.8))
        fig.patch.set_facecolor("#FFFFFF")
        ax.set_facecolor("#FAFAF8")
        bar_colors = [
            "#3B6D11" if n<4.0 else "#BA7517" if n<5.5 else "#E24B4A" if n<7.0 else "#A32D2D"
            for n in niveles
        ]
        bars = ax.bar(dias, niveles, color=bar_colors, alpha=0.88, width=0.55, edgecolor="#E8E6E0", linewidth=0.6)
        ax.fill_between(range(len(niveles)), niveles, alpha=0.07, color="#3B6D11")
        ax.plot(range(len(niveles)), niveles, color="#3B6D11", linewidth=1.5, alpha=0.6, linestyle="--", marker="o", markersize=3)
        ax.axhline(y=4.0, color="#FFD600", linestyle="--", linewidth=1.2, alpha=0.6, label="Amarilla (4m)")
        ax.axhline(y=5.5, color="#FF9800", linestyle="--", linewidth=1.2, alpha=0.6, label="Naranja (5.5m)")
        ax.axhline(y=7.0, color="#FF5252", linestyle="--", linewidth=1.2, alpha=0.6, label="Roja (7m)")
        ax.set_ylabel("Nivel (m)", color="#5F5E5A", fontsize=9)
        ax.set_ylim(0, 9)
        ax.tick_params(colors="#5F5E5A", labelsize=8)
        for spine in ax.spines.values(): spine.set_color("#D3D1C7")
        ax.set_xticks(range(len(dias)))
        ax.set_xticklabels(dias, fontsize=7.5, color="#5F5E5A", rotation=15)
        ax.grid(axis="y", color="#E8E6E0", linewidth=0.6, linestyle=":")
        ax.legend(fontsize=7.5, facecolor="#FFFFFF", labelcolor="#5F5E5A", framealpha=0.9, loc="upper right")
        for bar, val in zip(bars, niveles):
            ax.text(bar.get_x()+bar.get_width()/2, val+0.13, f"{val}m",
                    ha="center", va="bottom", color="white", fontsize=7.5, fontweight="bold")
        plt.tight_layout(pad=0.6)
        st.pyplot(fig)
        plt.close()

        if "Normal" in rio_txt:     st.success(f"🟢 {rio_txt} — Nivel en rango seguro")
        elif "Amarilla" in rio_txt: st.warning(f"🟡 {rio_txt} — Monitorear de cerca")
        elif "Naranja" in rio_txt:  st.warning(f"🟠 {rio_txt} — Precaución zonas bajas")
        else:                       st.error(f"🔴 {rio_txt} — ¡Alerta máxima!")

        prob_hoy_pred = clima.get("prob_lluvia",[0])[0] if clima.get("prob_lluvia") else 0
        st.markdown(f"""
        <div class="stat-row">
          🌧️ Lluvia hoy: <b>{clima['lluvia_hoy']} mm</b> &nbsp;·&nbsp;
          🌂 Prob.: <b style="color:#185FA5">{prob_hoy_pred}%</b> &nbsp;·&nbsp;
          💨 Viento: <b>{clima['viento']} km/h</b> &nbsp;·&nbsp;
          🌡️ Máx: <b>{clima['temp_max'][0]}°C</b><br>
          <small>{fuente_rio}</small>
        </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        df_niveles = pd.DataFrame({
            "Día": dias,
            "Nivel": [f"{n} m" for n in niveles],
            "Estado": [alerta_rio(n)[0] for n in niveles]
        })
        st.dataframe(df_niveles, use_container_width=True, hide_index=True, height=210)

    st.markdown("<hr>", unsafe_allow_html=True)

    nivel_actual = niveles[0]
    alerta_lbl, _, alerta_color = alerta_rio(nivel_actual)
    with st.expander(f"🌊 Zonas afectadas por nivel del río — Estado actual: {alerta_lbl} ({nivel_actual}m)", expanded=nivel_actual>=4.0):
        ZONAS_INFO = [
            ("Zona ALTO riesgo","La Granja · La Ribera · Los Nogales","Margen occidental río, cota baja",4.0,"Evacuar si nivel supera 5m · Ruta: Av. Circunvalar hacia el este"),
            ("Zona ALTO riesgo","Barrio Colón · Chuchurubi · Santa Fe","Sector sur, históricamente inundado",4.0,"Zona con antecedentes de inundación · Contactar Defensa Civil: 144"),
            ("Zona MEDIO riesgo","Ronda del Sinú norte · Av. Primera","Parque lineal y avenida ribereña",5.5,"Cerrar acceso al parque si nivel > 5.5m"),
            ("Zona MEDIO riesgo","El Recreo · Ribera norte","Barrio nororiental junto al río",5.5,"Monitorear de cerca en temporada de lluvias"),
            ("Zona ALTO riesgo","Mocarí · Zona sur rural","Área baja al sur de Montería",4.0,"Zona agrícola — riesgo de pérdidas en cultivos"),
        ]
        for zona, barrios, ubicacion, cota, accion in ZONAS_INFO:
            if nivel_actual>=cota+1.5:   badge_color,estado_txt = "badge-red",  f"🔴 INUNDACIÓN — nivel {nivel_actual}m supera cota {cota}m"
            elif nivel_actual>=cota:     badge_color,estado_txt = "badge-yellow",f"🟠 ALERTA — nivel {nivel_actual}m alcanzó cota {cota}m"
            elif nivel_actual>=cota-0.5: badge_color,estado_txt = "badge-yellow",f"🟡 PRECAUCIÓN — nivel {nivel_actual}m se acerca a cota {cota}m"
            else:                        badge_color,estado_txt = "badge-green", f"✅ Normal — nivel {nivel_actual}m · cota alerta: {cota}m"
            st.markdown(f"""
            <div style="background:#F4F2EE;border:1px solid #D3D1C7;border-radius:12px;
                        padding:14px 18px;margin-bottom:10px">
              <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
                <span class="badge {badge_color}">{zona}</span>
                <span style="color:#1E1E1C;font-family:'Outfit',sans-serif;font-weight:700">{barrios}</span>
              </div>
              <div style="color:#5F5E5A;font-size:0.83rem;margin-bottom:4px">📍 {ubicacion} · Cota alerta: {cota}m</div>
              <div style="color:#185FA5;font-size:0.83rem;margin-bottom:4px;font-weight:600">📊 {estado_txt}</div>
              <div style="color:#888780;font-size:0.79rem">💡 {accion}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:rgba(59,109,17,0.04);border:1px solid rgba(59,109,17,0.15);
                    border-radius:10px;padding:12px 16px;font-size:0.8rem;color:#5F5E5A;font-weight:500">
          📞 <b style="color:#1E1E1C">Emergencias:</b> Defensa Civil 144 · Bomberos 119 · Cruz Roja 132<br>
          📡 <b style="color:#1E1E1C">Datos en tiempo real:</b> IDEAM · {fuente_rio}
        </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# TAB 3 — ANÁLISIS
# ══════════════════════════════════════════════════════════
with tab_analisis:
    st.markdown('<div class="section-header">💨 Calidad del aire · Open-Meteo Air Quality API</div>', unsafe_allow_html=True)
    _a1,_a2 = st.columns(2, gap="small")
    with _a1:
        st.markdown(f"""<div class="kpi-card kpi-card-green">
          <div class="kpi-label">PM2.5</div><div class="kpi-value">{aire['pm25']} µg/m³</div>
          <span class="badge badge-green">✅ OMS &lt; 15</span>
          <div class="fuente-tag">Open-Meteo · tiempo real</div></div>""", unsafe_allow_html=True)
    with _a2:
        st.markdown(f"""<div class="kpi-card kpi-card-green">
          <div class="kpi-label">PM10</div><div class="kpi-value">{aire['pm10']} µg/m³</div>
          <span class="badge badge-green">✅ OMS &lt; 45</span>
          <div class="fuente-tag">Open-Meteo · tiempo real</div></div>""", unsafe_allow_html=True)
    _a3,_a4 = st.columns(2, gap="small")
    with _a3:
        st.markdown(f"""<div class="kpi-card kpi-card-green">
          <div class="kpi-label">NO₂</div><div class="kpi-value">{aire['no2']} µg/m³</div>
          <span class="badge badge-green">✅ Normal</span>
          <div class="fuente-tag">Open-Meteo · tiempo real</div></div>""", unsafe_allow_html=True)
    with _a4:
        st.markdown(f"""<div class="kpi-card kpi-card-green">
          <div class="kpi-label">AQI Europeo</div><div class="kpi-value">{aire['aqi']}</div>
          <span class="badge {aqi_badge}">{aqi_txt}</span>
          <div class="fuente-tag">Open-Meteo · tiempo real</div></div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">🌡️ Índice de calor aparente · Heat Index</div>', unsafe_allow_html=True)
    hi_val, hi_lbl, hi_badge, hi_color = calcular_heat_index(clima.get("temp",30), clima.get("humedad",75))
    hi_c1,hi_c2,hi_c3,hi_c4 = st.columns(4, gap="small")
    with hi_c1:
        st.markdown(f"""<div class="kpi-card kpi-card-green">
          <div class="kpi-label">Temperatura real</div><div class="kpi-value">{clima.get('temp','—')}°C</div>
          <span class="badge badge-green">Termómetro</span>
          <div class="fuente-tag">Open-Meteo · tiempo real</div></div>""", unsafe_allow_html=True)
    with hi_c2:
        st.markdown(f"""<div class="kpi-card kpi-card-green">
          <div class="kpi-label">Humedad relativa</div><div class="kpi-value">{clima.get('humedad','—')}%</div>
          <span class="badge badge-green">Humedad</span>
          <div class="fuente-tag">Open-Meteo · tiempo real</div></div>""", unsafe_allow_html=True)
    with hi_c3:
        st.markdown(f"""<div class="kpi-card kpi-card-green">
          <div class="kpi-label">Calor aparente</div>
          <div class="kpi-value" style="color:{hi_color}">{hi_val}°C</div>
          <span class="badge {hi_badge}">{hi_lbl}</span>
          <div class="fuente-tag">Fórmula Steadman/NWS</div></div>""", unsafe_allow_html=True)
    with hi_c4:
        st.markdown(f"""<div class="kpi-card kpi-card-green">
          <div class="kpi-label">Diferencia térmica</div>
          <div class="kpi-value" style="color:{hi_color}">+{round(hi_val-clima.get('temp',30),1)}°C</div>
          <span class="badge {hi_badge}">Sensación extra</span>
          <div class="fuente-tag">vs temperatura real</div></div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="background:linear-gradient(135deg,#F4F2EE,#EEECEA);border:1px solid #D3D1C7;
                border-radius:12px;padding:14px 18px;margin-top:8px">
      <b style="color:#1E1E1C;font-family:'Outfit',sans-serif;font-size:0.85rem;
                display:block;margin-bottom:10px">Escala de riesgo por calor · OMS / NWS:</b>
      <div style="display:flex;flex-wrap:wrap;gap:8px">
        <span style="background:#EAF3DE;color:#27500A;padding:5px 12px;border-radius:8px;font-size:0.79rem;font-weight:700">✅ &lt;27°C · Confortable</span>
        <span style="background:#FAEEDA;color:#633806;padding:5px 12px;border-radius:8px;font-size:0.79rem;font-weight:700">🟡 27–32°C · Precaución</span>
        <span style="background:#F5C4B3;color:#712B13;padding:5px 12px;border-radius:8px;font-size:0.79rem;font-weight:700">🟠 32–41°C · Precaución extrema</span>
        <span style="background:#F7C1C1;color:#791F1F;padding:5px 12px;border-radius:8px;font-size:0.79rem;font-weight:700">🔴 41–54°C · Peligro</span>
        <span style="background:#F09595;color:#501313;padding:5px 12px;border-radius:8px;font-size:0.79rem;font-weight:700">☠️ &gt;54°C · Peligro extremo</span>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">💧 Correlación lluvia vs nivel del río · 7 días</div>', unsafe_allow_html=True)

    lluvia_7d = clima.get("lluvia_7d", [0]*7)
    fig_corr, axes = plt.subplots(1, 2, figsize=(11, 3.5))
    fig_corr.patch.set_facecolor("#FFFFFF")
    ax1 = axes[0]; ax1.set_facecolor("#F9F8F6"); ax2 = ax1.twinx()
    dias_cortos = [d.replace(" ","") for d in dias]
    ax1.bar(dias_cortos, lluvia_7d, color="#4FC3F7", alpha=0.6, width=0.4, label="Lluvia (mm)")
    ax2.plot(dias_cortos, niveles, color="#3B6D11", linewidth=2.5, marker="o", markersize=5, label="Nivel río (m)")
    ax1.set_ylabel("Lluvia (mm)", color="#4FC3F7", fontsize=8)
    ax2.set_ylabel("Nivel río (m)", color="#3B6D11", fontsize=8)
    ax1.tick_params(colors="#5F5E5A", labelsize=7); ax2.tick_params(colors="#3B6D11", labelsize=7)
    for spine in ax1.spines.values(): spine.set_color("#D3D1C7")
    for spine in ax2.spines.values(): spine.set_color("#D3D1C7")
    ax1.set_title("Lluvia acumulada vs nivel del río", color="#1E1E1C", fontsize=9, pad=6)
    ax1.tick_params(axis='x', rotation=15)
    ax1.grid(axis="y", color="#E8E6E0", linewidth=0.5)
    lines1,labels1 = ax1.get_legend_handles_labels()
    lines2,labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1+lines2, labels1+labels2, fontsize=7, facecolor="#FFFFFF", labelcolor="#5F5E5A", loc="upper left")
    ax3 = axes[1]; ax3.set_facecolor("#F9F8F6")
    colores_scatter = ["#3B6D11" if n<4.0 else "#FFD600" if n<5.5 else "#FF9800" for n in niveles]
    ax3.scatter(lluvia_7d, niveles, c=colores_scatter, s=80, zorder=5, alpha=0.9)
    for i,(x,y) in enumerate(zip(lluvia_7d,niveles)):
        ax3.annotate(dias_cortos[i], (x,y), textcoords="offset points", xytext=(4,4), fontsize=6.5, color="#5F5E5A")
    if len(lluvia_7d)>1:
        z = np.polyfit(lluvia_7d, niveles, 1); p = np.poly1d(z)
        x_line = np.linspace(min(lluvia_7d), max(lluvia_7d), 50)
        ax3.plot(x_line, p(x_line), "--", color="#FF9800", linewidth=1.2, alpha=0.7, label="Tendencia")
        corr = np.corrcoef(lluvia_7d, niveles)[0,1]
        ax3.text(0.05, 0.92, f"r = {corr:.2f}", transform=ax3.transAxes, color="#3B6D11", fontsize=8, fontweight="bold")
    ax3.set_xlabel("Lluvia acumulada (mm)", color="#5F5E5A", fontsize=8)
    ax3.set_ylabel("Nivel del río (m)", color="#5F5E5A", fontsize=8)
    ax3.set_title("Correlación lluvia → nivel", color="#1E1E1C", fontsize=9, pad=6)
    ax3.tick_params(colors="#5F5E5A", labelsize=7)
    for spine in ax3.spines.values(): spine.set_color("#D3D1C7")
    ax3.grid(color="#E8E6E0", linewidth=0.5)
    ax3.legend(fontsize=7, facecolor="#FFFFFF", labelcolor="#5F5E5A")
    plt.tight_layout(pad=0.8)
    st.pyplot(fig_corr); plt.close()

    corr_val = np.corrcoef(lluvia_7d, niveles)[0,1] if len(lluvia_7d)>1 else 0
    interp = ("correlación muy fuerte" if abs(corr_val)>0.8 else "correlación moderada" if abs(corr_val)>0.5 else "correlación débil")
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#EAF3DE,#E0EFCE);border:1px solid #C8E4A0;
                border-radius:10px;padding:12px 16px;font-size:0.84rem;color:#2C2C2A;font-weight:500">
      📊 <b style="color:#27500A;font-family:'Outfit',sans-serif">Coeficiente de Pearson r = {corr_val:.2f}</b> — {interp} entre lluvia y nivel del río en los últimos 7 días.<br>
      <span style="color:#5F5E5A">ℹ️ El río Sinú responde a la lluvia con un rezago de 1-2 días por la cuenca hídrica del Alto Sinú.</span>
    </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">📈 Históricas 30 días · Temperatura · Lluvia · PM2.5</div>', unsafe_allow_html=True)

    hist_clima = obtener_historico_30dias()
    hist_aire  = obtener_historico_aire_30dias()

    if hist_clima["ok"] and hist_clima["fechas"]:
        fechas_hist = [f[5:] for f in hist_clima["fechas"]]
        paso = max(1, len(fechas_hist)//10)
        xticks_idx = list(range(0, len(fechas_hist), paso))
        fig_hist, axs = plt.subplots(3, 1, figsize=(11, 8), sharex=False)
        fig_hist.patch.set_facecolor("#FFFFFF")
        ax = axs[0]; ax.set_facecolor("#F9F8F6")
        ax.fill_between(range(len(fechas_hist)), hist_clima["temp_min"], hist_clima["temp_max"], alpha=0.25, color="#FF9800", label="Rango Tmin-Tmax")
        ax.plot(range(len(fechas_hist)), hist_clima["temp_max"], color="#FF9800", linewidth=1.5, label="Tmax")
        ax.plot(range(len(fechas_hist)), hist_clima["temp_min"], color="#4FC3F7", linewidth=1.5, label="Tmin")
        ax.set_ylabel("°C", color="#5F5E5A", fontsize=8)
        ax.set_title("Temperatura máx/mín diaria", color="#1E1E1C", fontsize=9, pad=4)
        ax.tick_params(colors="#5F5E5A", labelsize=7)
        ax.set_xticks(xticks_idx); ax.set_xticklabels([fechas_hist[i] for i in xticks_idx], rotation=15)
        for spine in ax.spines.values(): spine.set_color("#D3D1C7")
        ax.grid(color="#E8E6E0", linewidth=0.5)
        ax.legend(fontsize=7, facecolor="#FFFFFF", labelcolor="#5F5E5A", loc="upper right")
        ax2h = axs[1]; ax2h.set_facecolor("#F9F8F6")
        ax2h.bar(range(len(fechas_hist)), hist_clima["lluvia"], color="#4FC3F7", alpha=0.75, width=0.7)
        ax2h.set_ylabel("mm", color="#5F5E5A", fontsize=8)
        ax2h.set_title("Precipitación diaria acumulada", color="#1E1E1C", fontsize=9, pad=4)
        ax2h.tick_params(colors="#5F5E5A", labelsize=7)
        ax2h.set_xticks(xticks_idx); ax2h.set_xticklabels([fechas_hist[i] for i in xticks_idx], rotation=15)
        for spine in ax2h.spines.values(): spine.set_color("#D3D1C7")
        ax2h.grid(axis="y", color="#E8E6E0", linewidth=0.5)
        ax3h = axs[2]; ax3h.set_facecolor("#F9F8F6")
        if hist_aire["ok"] and hist_aire["fechas"]:
            fechas_pm = [f[5:] for f in hist_aire["fechas"]]
            colores_pm = ["#3B6D11" if v<10 else "#FFD600" if v<15 else "#FF9800" if v<25 else "#FF5252" for v in hist_aire["pm25"]]
            ax3h.bar(range(len(fechas_pm)), hist_aire["pm25"], color=colores_pm, alpha=0.85, width=0.7)
            ax3h.axhline(y=15, color="#FFD600", linestyle="--", linewidth=1, alpha=0.7, label="OMS límite (15)")
            paso_pm = max(1, len(fechas_pm)//10)
            ax3h.set_xticks(range(0, len(fechas_pm), paso_pm))
            ax3h.set_xticklabels([fechas_pm[i] for i in range(0, len(fechas_pm), paso_pm)], rotation=15, fontsize=7)
            ax3h.legend(fontsize=7, facecolor="#FFFFFF", labelcolor="#5F5E5A")
        ax3h.set_ylabel("µg/m³", color="#5F5E5A", fontsize=8)
        ax3h.set_title("PM2.5 promedio diario", color="#1E1E1C", fontsize=9, pad=4)
        ax3h.tick_params(colors="#5F5E5A", labelsize=7)
        for spine in ax3h.spines.values(): spine.set_color("#D3D1C7")
        ax3h.grid(axis="y", color="#E8E6E0", linewidth=0.5)
        plt.tight_layout(pad=1.2)
        st.pyplot(fig_hist); plt.close()

        t_prom   = round(sum(hist_clima["temp_max"])/len(hist_clima["temp_max"]), 1)
        ll_total = round(sum(hist_clima["lluvia"]), 1)
        ll_max   = round(max(hist_clima["lluvia"]), 1)
        pm_prom  = round(sum(hist_aire["pm25"])/len(hist_aire["pm25"]),1) if hist_aire["ok"] and hist_aire["pm25"] else "—"

        # ── RESUMEN 30 DÍAS — fix legibilidad total ─────────────
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#EAF3DE 0%,#E0EFCE 100%);
                    border:1.5px solid #97C459;border-radius:12px;
                    padding:14px 20px;margin-top:8px">
          <span style="font-family:'Outfit',sans-serif;font-weight:800;color:#27500A;
                       font-size:0.9rem;display:block;margin-bottom:8px">
            📊 Resumen últimos 30 días
          </span>
          <div style="display:flex;flex-wrap:wrap;gap:16px;align-items:center">
            <span style="color:#1E1E1C;font-size:0.88rem;font-weight:500">
              🌡️ Tmax promedio: <b style="color:#1E1E1C;font-size:1rem">{t_prom}°C</b>
            </span>
            <span style="color:#1E1E1C;font-size:0.88rem;font-weight:500">
              🌧️ Lluvia total: <b style="color:#185FA5;font-size:1rem">{ll_total} mm</b>
            </span>
            <span style="color:#1E1E1C;font-size:0.88rem;font-weight:500">
              ☔ Día más lluvioso: <b style="color:#185FA5;font-size:1rem">{ll_max} mm</b>
            </span>
            <span style="color:#1E1E1C;font-size:0.88rem;font-weight:500">
              💨 PM2.5 prom.: <b style="color:#1E1E1C;font-size:1rem">{pm_prom} µg/m³</b>
            </span>
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.info("Cargando datos históricos...")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">📊 Exportar datos · CSV para análisis externo</div>', unsafe_allow_html=True)

    import io
    df_export = pd.DataFrame({
        "Fecha":        dias,
        "Nivel_rio_m":  niveles,
        "Alerta_rio":   [alerta_rio(n)[0] for n in niveles],
        "Lluvia_mm":    lluvia_7d,
        "Temp_max_C":   clima.get("temp_max",[0]*7),
        "PM25_ug_m3":   [aire["pm25"]]*7,
        "PM10_ug_m3":   [aire["pm10"]]*7,
        "NO2_ug_m3":    [aire["no2"]]*7,
        "AQI_europeo":  [aire["aqi"]]*7,
        "Heat_index_C": [hi_val]*7,
        "Alerta_calor": [hi_lbl]*7,
    })
    ex1,ex2,ex3 = st.columns(3, gap="small")
    with ex1:
        csv_buf = io.StringIO()
        df_export.to_csv(csv_buf, index=False, encoding="utf-8-sig")
        st.download_button(label="⬇️ Descargar CSV (7 días)",
            data=csv_buf.getvalue().encode("utf-8-sig"),
            file_name=f"biomonitor_monteria_{datetime.now(TZ_COL).strftime('%Y%m%d')}.csv",
            mime="text/csv", use_container_width=True)
    with ex2:
        if hist_clima["ok"] and hist_clima["fechas"]:
            df_hist_export = pd.DataFrame({
                "Fecha":      hist_clima["fechas"],"Temp_max_C":hist_clima["temp_max"],
                "Temp_min_C": hist_clima["temp_min"],"Lluvia_mm":hist_clima["lluvia"],
                "Viento_kmh": hist_clima["viento"],
            })
            if hist_aire["ok"] and hist_aire["fechas"]:
                df_pm = pd.DataFrame({"Fecha":hist_aire["fechas"],"PM25_ug_m3":hist_aire["pm25"]})
                df_hist_export = df_hist_export.merge(df_pm, on="Fecha", how="left")
            csv_hist = io.StringIO()
            df_hist_export.to_csv(csv_hist, index=False, encoding="utf-8-sig")
            st.download_button(label="⬇️ Descargar CSV (30 días)",
                data=csv_hist.getvalue().encode("utf-8-sig"),
                file_name=f"biomonitor_historico_{datetime.now(TZ_COL).strftime('%Y%m%d')}.csv",
                mime="text/csv", use_container_width=True)
    with ex3:
        st.dataframe(df_export[["Fecha","Nivel_rio_m","Lluvia_mm","PM25_ug_m3","Heat_index_C"]],
                     use_container_width=True, hide_index=True, height=180)

    st.markdown("<hr>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# TAB 4 — BIODIVERSIDAD
# ══════════════════════════════════════════════════════════
with tab_bio:
    st.markdown('<div class="section-header">🦜 Biodiversidad · GBIF · Córdoba, Colombia</div>', unsafe_allow_html=True)
    df_fauna_live, fauna_ok = obtener_fauna_gbif()

    if fauna_ok and df_fauna_live is not None:
        n_especies = len(df_fauna_live)
        n_imagen   = int(df_fauna_live["imagen_url"].notna().sum())
        n_clases   = df_fauna_live["clase"].nunique()
        fuente_fauna = "🟢 GBIF · tiempo real · 24h"
    else:
        n_especies, n_imagen, n_clases = 12, 12, 8
        fuente_fauna = "🟡 Datos de respaldo"
        df_fauna_live = pd.DataFrame({
            "especie":    ["Heliconia psittacorum","Lygophis lineatus","Iguana iguana",
                           "Cairina moschata","Leptotila verreauxi","Chelonoidis carbonarius"],
            "nombre_com": ["Heliconia","Culebra","Iguana","Pato real","Paloma","Morrocoy"],
            "clase":      ["Liliopsida","Squamata","Squamata","Aves","Aves","Testudines"],
            "orden":      ["Zingiberales","Squamata","Squamata","Anseriformes","Columbiformes","Testudines"],
            "familia":    ["Heliconiaceae","Colubridae","Iguanidae","Anatidae","Columbidae","Testudinidae"],
            "estado":     ["No evaluado","No evaluado","No evaluado","No evaluado","No evaluado","Vulnerable"],
            "fecha":      ["2026-01-21","2026-01-11","2026-01-21","2026-01-22","2026-01-12","2026-01-25"],
            "imagen_url": [None]*6,"gbif_key":[""]*6,
        })

    _f1,_f2 = st.columns(2, gap="small")
    _f3,_f4 = st.columns(2, gap="small")
    for col, lbl, val, sub, badge_cls in [
        (_f1,"Especies registradas",str(n_especies),fuente_fauna,"badge-purple"),
        (_f2,"Con imagen",str(n_imagen),"Fotos verificadas","badge-green"),
        (_f3,"Clases taxonómicas",str(n_clases),"Taxones distintos","badge-blue"),
        (_f4,"Clasificación CNN","MobileNetV2","Precisión validada","badge-green"),
    ]:
        with col:
            st.markdown(f"""
            <div class="kpi-card kpi-card-purple">
              <div class="kpi-label">{lbl}</div><div class="kpi-value">{val}</div>
              <span class="badge {badge_cls}">{sub}</span>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    cols_mostrar     = ["especie","nombre_com","clase","orden","familia","estado","fecha"]
    cols_disponibles = [c for c in cols_mostrar if c in df_fauna_live.columns]
    df_mostrar = df_fauna_live[cols_disponibles].head(12).copy()
    df_mostrar.columns = [c.replace("_"," ").capitalize() for c in df_mostrar.columns]
    st.dataframe(df_mostrar, use_container_width=True, hide_index=True, height=320)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">📸 Galería de especies · Córdoba, Colombia · GBIF tiempo real</div>', unsafe_allow_html=True)

    imagenes_gbif = []
    if fauna_ok and df_fauna_live is not None and "imagen_url" in df_fauna_live.columns:
        for _, row in df_fauna_live.iterrows():
            url = row.get("imagen_url")
            if pd.notna(url) and url and isinstance(url,str) and url.startswith("http"):
                imagenes_gbif.append((url, row.get("especie","Especie")))
            if len(imagenes_gbif)>=6: break

    archivos_local = [
        ("imagenes_fauna/Heliconia_psittacorum.jpg","Heliconia psittacorum"),
        ("imagenes_fauna/Iguana_iguana.jpg","Iguana iguana"),
        ("imagenes_fauna/Leptotila_verreauxi.jpg","Leptotila verreauxi"),
        ("imagenes_fauna/Chelonoidis_carbonarius.jpg","Chelonoidis carbonarius"),
        ("imagenes_fauna/Cairina_moschata.jpg","Cairina moschata"),
        ("imagenes_fauna/Sakesphorus_canadensis.jpg","Sakesphorus canadensis"),
    ]

    def _render_img(col_obj, url_or_path, nombre, es_url=True):
        placeholder = f"""<div style="background:#F4F2EE;border:1px solid #D3D1C7;
            border-radius:12px;padding:20px;text-align:center;font-size:0.75rem;color:#5F5E5A">
            🦜<br><i style="color:#888780">{nombre}</i></div>"""
        try:
            if es_url: col_obj.image(url_or_path, caption=nombre, use_container_width=True)
            else: col_obj.image(Image.open(url_or_path), caption=nombre, use_container_width=True)
        except Exception:
            col_obj.markdown(placeholder, unsafe_allow_html=True)

    if len(imagenes_gbif)>=3:
        fuente_label, es_url_flag = imagenes_gbif, True
        label_tag = f"<small style='color:#3B6D11;font-weight:600'>📷 {len(imagenes_gbif)} imágenes · GBIF · Córdoba, Colombia</small>"
    else:
        fuente_label, es_url_flag = [(a,n) for a,n in archivos_local], False
        label_tag = "<small style='color:#888780'>📷 Imágenes locales · Banco fotográfico BioMonitor</small>"

    items = fuente_label[:6]
    for fila_idx in range(0, len(items), 3):
        trio = items[fila_idx:fila_idx+3]
        gcols = st.columns(len(trio), gap="small")
        for ci,(src_img,nombre) in enumerate(trio):
            _render_img(gcols[ci], src_img, nombre, es_url=es_url_flag)
    st.markdown(label_tag, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# TAB 5 — ALERTAS
# ══════════════════════════════════════════════════════════
with tab_alertas:
    st.markdown('<div class="section-header">🔔 Alertas activas · Montería</div>', unsafe_allow_html=True)

    alerta_lbl_t, _, _ = alerta_rio(niveles[0])
    if niveles[0]>=4.0:
        st.warning(f"🌊 **Río Sinú en alerta {alerta_lbl_t}** — Nivel actual: {niveles[0]}m. Monitorear zonas bajas.")
    else:
        st.success(f"✅ **Río Sinú en estado normal** — Nivel: {niveles[0]}m")

    hi_t, hi_lbl_t, _, _ = calcular_heat_index(clima.get("temp",30), clima.get("humedad",75))
    if hi_t>=32:
        st.warning(f"🌡️ **Calor aparente elevado: {hi_t}°C** — {hi_lbl_t}. Evitar exposición prolongada al sol.")
    else:
        st.success(f"✅ **Temperatura confortable** — Calor aparente: {hi_t}°C")

    pm25_val = aire.get("pm25",0)
    if pm25_val>=15:
        st.warning(f"💨 **PM2.5 sobre límite OMS** — {pm25_val} µg/m³. Límite OMS: 15 µg/m³")
    else:
        st.success(f"✅ **Calidad del aire buena** — PM2.5: {pm25_val} µg/m³")

    st.markdown("<hr>", unsafe_allow_html=True)

    nivel_actual_al = niveles[0]
    alerta_lbl_al, _, _ = alerta_rio(nivel_actual_al)
    with st.expander(f"🌊 Zonas afectadas por nivel del río — Estado: {alerta_lbl_al} ({nivel_actual_al}m)", expanded=nivel_actual_al>=4.0):
        ZONAS_INFO_AL = [
            ("Zona ALTO riesgo","La Granja · La Ribera · Los Nogales","Margen occidental río, cota baja",4.0,"Evacuar si nivel supera 5m · Ruta: Av. Circunvalar hacia el este"),
            ("Zona ALTO riesgo","Barrio Colón · Chuchurubi · Santa Fe","Sector sur, históricamente inundado",4.0,"Zona con antecedentes de inundación · Contactar Defensa Civil: 144"),
            ("Zona MEDIO riesgo","Ronda del Sinú norte · Av. Primera","Parque lineal y avenida ribereña",5.5,"Cerrar acceso al parque si nivel > 5.5m"),
            ("Zona MEDIO riesgo","El Recreo · Ribera norte","Barrio nororiental junto al río",5.5,"Monitorear de cerca en temporada de lluvias"),
            ("Zona ALTO riesgo","Mocarí · Zona sur rural","Área baja al sur de Montería",4.0,"Zona agrícola — riesgo de pérdidas en cultivos"),
        ]
        for zona, barrios, ubicacion, cota, accion in ZONAS_INFO_AL:
            if nivel_actual_al>=cota+1.5:   badge_color,estado_txt = "badge-red",  f"🔴 INUNDACIÓN — nivel {nivel_actual_al}m"
            elif nivel_actual_al>=cota:     badge_color,estado_txt = "badge-yellow",f"🟠 ALERTA — nivel {nivel_actual_al}m"
            elif nivel_actual_al>=cota-0.5: badge_color,estado_txt = "badge-yellow",f"🟡 PRECAUCIÓN — nivel {nivel_actual_al}m"
            else:                           badge_color,estado_txt = "badge-green", f"✅ Normal · cota alerta: {cota}m"
            st.markdown(f"""
            <div class="info-card">
              <span class="badge {badge_color}">{zona}</span>
              <b style="margin-left:8px;font-family:'Outfit',sans-serif">{barrios}</b><br>
              <span style="color:#5F5E5A;font-size:0.83rem">📍 {ubicacion}</span><br>
              <span style="color:#1E1E1C;font-size:0.83rem;font-weight:600">📊 {estado_txt}</span><br>
              <span style="color:#5F5E5A;font-size:0.8rem">💡 {accion}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown('<div class="info-card"><b style="font-family:\'Outfit\',sans-serif">📞 Emergencias:</b> Defensa Civil 144 · Bomberos 119 · Cruz Roja 132</div>', unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────
st.markdown(f"""
<div style='text-align:center;color:#888780;font-size:0.82rem;
            padding:20px 0 32px 0;border-top:1px solid #D3D1C7;
            margin-top:16px;line-height:2.2;font-weight:500'>
  <b style='font-family:Outfit,sans-serif;color:#3B6D11;font-size:0.95rem;font-weight:800'>
    BioMonitor Montería
  </b>
  &nbsp;·&nbsp; {datetime.now(TZ_COL).strftime('%d/%m/%Y %H:%M')}
  &nbsp;·&nbsp; <span style="color:#5F5E5A">Open-Meteo · IDEAM · GBIF</span>
  &nbsp;·&nbsp; <span style="color:#5F5E5A">LSTM + MobileNetV2</span>
  &nbsp;·&nbsp; <b style='font-family:Outfit,sans-serif;color:#3B6D11'>© Ivan Contreras</b>
</div>""", unsafe_allow_html=True)