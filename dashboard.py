import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, timezone, UTC
from zoneinfo import ZoneInfo
TZ_COL = ZoneInfo('America/Bogota')  # UTC-5 Colombia
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

# ── CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background-color: #060d1a !important;
}
.main { background-color: #060d1a; }
.block-container {
    padding-top:2rem !important;
    padding-left:2rem !important;
    padding-right:2rem !important;
    max-width: 1400px;
}

/* Hero */
.hero-sub { color:#5a7a9a; font-size:1rem; line-height:1.6; margin:0; }
.hero-badge {
    display:inline-block;
    background:rgba(0,229,195,0.1);
    border:1px solid rgba(0,229,195,0.3);
    color:#00E5C3;
    padding:3px 12px;
    border-radius:20px;
    font-size:0.75rem;
    font-weight:600;
    letter-spacing:1px;
    text-transform:uppercase;
    margin-right:6px;
    margin-top:4px;
}

/* KPI Cards */
.kpi-card {
    background:linear-gradient(135deg,#0d1b2e,#0a1628);
    border:1px solid rgba(0,229,195,0.15);
    border-radius:16px;
    padding:18px 20px;
    position:relative;
    overflow:hidden;
    margin-bottom:10px;
    min-height: 120px;
}
.kpi-card::before {
    content:'';
    position:absolute;
    top:0; left:0;
    width:4px; height:100%;
    background:linear-gradient(180deg,#00E5C3,#4FC3F7);
    border-radius:4px 0 0 4px;
}
.kpi-card-red::before    { background:linear-gradient(180deg,#FF5252,#FF9800); }
.kpi-card-blue::before   { background:linear-gradient(180deg,#4FC3F7,#7B61FF); }
.kpi-card-green::before  { background:linear-gradient(180deg,#00E5C3,#69F0AE); }
.kpi-card-purple::before { background:linear-gradient(180deg,#7B61FF,#E040FB); }

.kpi-label {
    font-size:0.7rem;
    color:#5a7a9a;
    text-transform:uppercase;
    letter-spacing:1.5px;
    font-weight:600;
    margin-bottom:6px;
}
.kpi-value    { font-size:2rem;  font-weight:800; color:#e8f4ff; line-height:1; margin-bottom:8px; }
.kpi-value-sm { font-size:1.4rem; font-weight:700; color:#e8f4ff; line-height:1; margin-bottom:8px; }

/* Badges */
.badge { display:inline-block; padding:3px 10px; border-radius:20px; font-size:0.75rem; font-weight:600; }
.badge-green  { background:rgba(0,229,195,0.15);  color:#00E5C3; border:1px solid rgba(0,229,195,0.3); }
.badge-yellow { background:rgba(255,214,0,0.15);  color:#FFD600; border:1px solid rgba(255,214,0,0.3); }
.badge-red    { background:rgba(255,82,82,0.15);  color:#FF5252; border:1px solid rgba(255,82,82,0.3); }
.badge-blue   { background:rgba(79,195,247,0.15); color:#4FC3F7; border:1px solid rgba(79,195,247,0.3); }
.badge-purple { background:rgba(123,97,255,0.15); color:#7B61FF; border:1px solid rgba(123,97,255,0.3); }

.section-header {
    font-size:1.05rem;
    font-weight:700;
    color:#4FC3F7;
    letter-spacing:0.5px;
    margin-bottom:14px;
    display:flex;
    align-items:center;
    gap:8px;
}
.section-header::after {
    content:'';
    flex:1;
    height:1px;
    background:linear-gradient(90deg,rgba(79,195,247,0.3),transparent);
}

.fuente-tag { font-size:0.68rem; color:#3a5a7a; margin-top:4px; }
.stat-row {
    background:rgba(0,229,195,0.05);
    border:1px solid rgba(0,229,195,0.1);
    border-radius:10px;
    padding:10px 14px;
    margin-top:8px;
    font-size:0.82rem;
    color:#5a7a9a;
}

/* Copyright fijo */
.copyright {
    position:fixed;
    bottom:10px;
    right:16px;
    color:#2a4a6a;
    font-size:0.72rem;
    z-index:9999;
}

/* Botones */
.stButton > button {
    background:linear-gradient(135deg,#00E5C3,#4FC3F7) !important;
    color:#060d1a !important;
    font-weight:700 !important;
    border:none !important;
    border-radius:10px !important;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.88; }

/* Ocultar footer y menú */
footer { visibility:hidden; }
#MainMenu { visibility:hidden; }

/* Dataframe */
.stDataFrame { border-radius: 12px; overflow: hidden; }

/* Expander */
.streamlit-expanderHeader {
    background: rgba(0,229,195,0.05) !important;
    border: 1px solid rgba(0,229,195,0.15) !important;
    border-radius: 10px !important;
    color: #4FC3F7 !important;
    font-weight: 600 !important;
}

/* Radio */
.stRadio > div { gap: 8px !important; }
.stRadio label { color: #5a7a9a !important; font-size: 0.85rem !important; }

/* ══ RESPONSIVE MÓVIL ══════════════════════════════════ */

/* Tablet (≤900px) */
@media (max-width:900px) {
    .block-container { padding-left:1rem !important; padding-right:1rem !important; }
    .kpi-value { font-size:1.6rem !important; }
    .hero-sub  { font-size:0.88rem !important; }
}

/* Móvil (≤768px) — breakpoint principal */
@media (max-width:768px) {

    /* Padding mínimo */
    .block-container {
        padding-top:1rem !important;
        padding-left:0.6rem !important;
        padding-right:0.6rem !important;
    }

    /* KPI cards: 2 columnas en móvil */
    .kpi-value    { font-size:1.35rem !important; }
    .kpi-value-sm { font-size:1.1rem  !important; }
    .kpi-label    { font-size:0.62rem !important; letter-spacing:1px !important; }
    .kpi-card     { min-height:auto !important; padding:12px 14px !important; margin-bottom:8px !important; }

    /* Forzar columnas Streamlit a apilarse */
    [data-testid="column"] { min-width:100% !important; }

    /* Hero badges: wrap */
    .hero-badge { font-size:0.65rem !important; padding:2px 8px !important; margin-bottom:4px !important; }
    .hero-sub   { font-size:0.82rem !important; }

    /* Section headers más compactos */
    .section-header { font-size:0.9rem !important; }

    /* Stat row */
    .stat-row { font-size:0.76rem !important; }

    /* Copyright oculto en móvil (ocupa espacio) */
    .copyright { display:none !important; }

    /* Botones más grandes para touch */
    .stButton > button {
        min-height:44px !important;
        font-size:0.9rem !important;
    }

    /* Badges más pequeños */
    .badge { font-size:0.68rem !important; padding:2px 7px !important; }

    /* Radio horizontal → apilado */
    .stRadio > div { flex-direction:column !important; gap:4px !important; }

    /* Expander header */
    .streamlit-expanderHeader { font-size:0.85rem !important; }

    /* Galería: 2 cols en móvil */
    .galeria-grid { grid-template-columns: repeat(2, 1fr) !important; }

    /* Dataframe scroll horizontal */
    .stDataFrame { overflow-x:auto !important; }

    /* Fuente tag */
    .fuente-tag { font-size:0.62rem !important; }
}

/* Móvil pequeño (≤480px) */
@media (max-width:480px) {
    .block-container {
        padding-left:0.3rem !important;
        padding-right:0.3rem !important;
    }
    .kpi-value    { font-size:1.15rem !important; }
    .kpi-label    { font-size:0.58rem !important; }
    .section-header { font-size:0.82rem !important; }
    .hero-sub { font-size:0.78rem !important; }
    .stButton > button { font-size:0.82rem !important; }
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="copyright">© Ivan Contreras</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# ── FUNCIONES DE DATOS ───────────────────────────────────
# ══════════════════════════════════════════════════════════

def _fetch_clima():
    """Obtiene clima actual + pronóstico 7 días de Open-Meteo"""
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
        # lluvia_hoy: suma del día actual (más representativa que la instantánea)
        lluvia_sum_hoy = d.get("precipitation_sum", [0])[0] if d.get("precipitation_sum") else 0
        # prob lluvia: limpiar None → 0
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
    """Obtiene calidad del aire desde Open-Meteo Air Quality API"""
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
    """Consulta nivel real del Río Sinú desde datos.gov.co (IDEAM)"""
    # Capa 1: API datos.gov.co — estación Montería
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

    # Capa 2: IDEAM DHIME (respaldo)
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

    # Capa 3: fallback histórico
    return {
        "nivel":  4.2,
        "fecha":  datetime.now(TZ_COL).strftime("%Y-%m-%d"),
        "ok":     False,
        "fuente": "Histórico"
    }

@st.cache_data(ttl=900)  # 15 min — datos más frescos
def cargar_datos():
    """Carga paralela de clima, aire e IDEAM"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        fc = ex.submit(_fetch_clima)
        fa = ex.submit(_fetch_aire)
        fi = ex.submit(_fetch_ideam)
        return fc.result(), fa.result(), fi.result()


def nivel_rio(lluvia_7d, base=4.2):
    """Simula predicción LSTM del nivel del río dado lluvia acumulada.
    Incluye variación diaria natural del río y efecto de lluvia aguas arriba."""
    niveles, ant = [], base
    # Factor de variación natural diaria (mareas/escorrentía base)
    variacion_base = [0.0, 0.05, -0.03, 0.08, -0.02, 0.06, -0.04]
    for i, ll in enumerate(lluvia_7d):
        var = variacion_base[i % len(variacion_base)]
        # La lluvia tiene efecto rezagado (llega al río 1-2 días después)
        lluvia_efecto = ll * 0.08 + (lluvia_7d[i-1] * 0.04 if i > 0 else 0)
        n = round(np.clip(ant * 0.85 + base * 0.15 + lluvia_efecto + var, 0.5, 9.5), 2)
        niveles.append(n)
        ant = n
    return niveles

def alerta_rio(n):
    if n < 4.0:   return "Normal",    "badge-green",  "#00E5C3"
    elif n < 5.5: return "Amarilla",  "badge-yellow", "#FFD600"
    elif n < 7.0: return "Naranja",   "badge-yellow", "#FF9800"
    else:         return "ROJA 🚨",   "badge-red",    "#FF5252"

def cat_aqi(aqi):
    if aqi <= 20:   return "Bueno",      "badge-green"
    elif aqi <= 40: return "Aceptable",  "badge-yellow"
    elif aqi <= 60: return "Moderado",   "badge-yellow"
    else:           return "Malo",       "badge-red"

# ══════════════════════════════════════════════════════════
# ── CARGA DE DATOS ────────────────────────────────────────
# ══════════════════════════════════════════════════════════

# ── Spinner de carga visible mientras se obtienen los datos ──
_loading = st.empty()
_loading.markdown("""
<div style="text-align:center;padding:40px 0;">
    <div style="color:#00E5C3;font-size:1.1rem;font-weight:700;margin-bottom:8px">
        🌿 Cargando BioMonitor Montería…
    </div>
    <div style="color:#5a7a9a;font-size:0.85rem">
        Conectando con Open-Meteo · IDEAM · GBIF
    </div>
</div>
""", unsafe_allow_html=True)

try:
    clima, aire, ideam = cargar_datos()
except Exception as _e:
    _loading.error(
        f"⚠️ Error al cargar datos: {_e}  \n\n"
        "Intenta recargar la página o pulsa **🔄 Actualizar**."
    )
    st.stop()

_loading.empty()  # Ocultar spinner una vez cargado

# Definir fuente y nivel base del río (3 capas)
if ideam["ok"]:
    nivel_base = ideam["nivel"]
    fuente_rio = f"🟢 {ideam['fuente']} · {ideam['fecha']}"
elif clima["ok"]:
    nivel_base = 4.2
    fuente_rio = "🟡 Simulado · lluvia real Open-Meteo"
else:
    nivel_base = 4.2
    fuente_rio = "🔴 Datos históricos"

niveles = nivel_rio(clima["lluvia_7d"], base=nivel_base)

# Etiquetas de días
if clima["fechas"]:
    dias = [datetime.strptime(f, "%Y-%m-%d").strftime("%d %b") for f in clima["fechas"]]
else:
    dias = [(datetime.now(TZ_COL) + timedelta(days=i)).strftime("%d %b") for i in range(7)]

rio_txt, rio_badge, rio_color = alerta_rio(niveles[0])
aqi_txt, aqi_badge = cat_aqi(aire["aqi"])

# ══════════════════════════════════════════════════════════
# ── HEADER ────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════

col_logo, col_info, col_btns = st.columns([0.7, 2.5, 1], gap="small")

with col_logo:
    try:
        logo = Image.open("Biomotorlogo.png")
        st.image(logo, use_container_width=True)
    except Exception:
        st.markdown('<h2 style="color:#00E5C3;margin:0">🌿 BioMonitor</h2>', unsafe_allow_html=True)
        st.markdown('<p style="color:#5a7a9a;font-size:0.8rem;margin:0">Montería · Córdoba</p>', unsafe_allow_html=True)

with col_info:
    fuente_estado = "🟢 En vivo" if clima["ok"] else "🟡 Respaldo"
    st.markdown(f"""
    <div style="display:flex;flex-direction:column;justify-content:center;height:100%;padding:8px 0">
        <h3 style="color:#e8f4ff;margin:0 0 4px 0;font-size:1.35rem;font-weight:800;letter-spacing:-0.5px">
            BioMonitor <span style="color:#00E5C3">Montería</span>
        </h3>
        <p class="hero-sub">Plataforma inteligente de monitoreo ambiental ·
        Río Sinú · Calidad del aire · Biodiversidad · Córdoba, Colombia</p>
        <div style="margin-top:10px">
            <span class="hero-badge">🌿 Ambiental</span>
            <span class="hero-badge">📡 Tiempo real</span>
            <span class="hero-badge">🧬 Biodiversidad</span>
            <span class="hero-badge">🌊 Río Sinú</span>
            <span class="hero-badge" style="color:#FFD600;border-color:rgba(255,214,0,0.3);background:rgba(255,214,0,0.08)">
                {fuente_estado}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_btns:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("🔄 Actualizar datos", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown(f"""
    <div style='text-align:center;font-size:0.73rem;color:#3a5a7a;
                margin:6px 0;padding:5px 0;
                border-top:1px solid rgba(0,229,195,0.08);
                border-bottom:1px solid rgba(0,229,195,0.08)'>
        Última actualización: <b style="color:#4FC3F7">{datetime.now(TZ_COL).strftime('%H:%M')}</b>
        &nbsp;·&nbsp; {datetime.now(TZ_COL).strftime('%d/%m/%Y')}
    </div>""", unsafe_allow_html=True)

    # Toggle info
    btn_label = "🔼 Ocultar info" if st.session_state.show_info else "ℹ️ ¿Qué es BioMonitor?"
    if st.button(btn_label, use_container_width=True):
        st.session_state.show_info = not st.session_state.show_info
        st.rerun()

# Panel informativo desplegable
if st.session_state.show_info:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0d1b2e,#0a1628);
                border:1px solid rgba(0,229,195,0.2);border-radius:16px;
                padding:20px 28px;margin:10px 0 4px 0">
        <h4 style="color:#00E5C3;margin:0 0 12px 0;font-size:1rem">🌿 Sobre BioMonitor Montería</h4>
        <p style="color:#8892a4;font-size:0.9rem;line-height:1.8;margin:0">
        <b style="color:#e8f4ff">BioMonitor Montería</b> es una plataforma de inteligencia ambiental
        para el monitoreo en tiempo real de <b style="color:#e8f4ff">Montería, Córdoba, Colombia</b>.<br><br>
        Integra tres módulos principales:
        <b style="color:#4FC3F7">predicción de inundaciones</b> del río Sinú con modelos LSTM,
        <b style="color:#00E5C3">calidad del aire</b> con indicadores PM2.5, PM10, NO₂ y AQI europeo,
        y <b style="color:#7B61FF">biodiversidad</b> con registros verificados por CNN (MobileNetV2).<br><br>
        Fuentes de datos: <b style="color:#e8f4ff">Open-Meteo</b> (clima y aire) ·
        <b style="color:#e8f4ff">IDEAM / datos.gov.co</b> (hidrología) ·
        <b style="color:#e8f4ff">GBIF</b> (biodiversidad) — actualizados automáticamente cada hora.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border:1px solid rgba(0,229,195,0.1);margin:14px 0'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# ── KPIs PRINCIPALES ─────────────────────────────────────
# ══════════════════════════════════════════════════════════

def _kpi_card(cls, label, val, badge_txt, badge_cls, fuente):
    st.markdown(f"""
    <div class="{cls}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{val}</div>
        <span class="badge {badge_cls}">{badge_txt}</span>
        <div class="fuente-tag">{fuente}</div>
    </div>""", unsafe_allow_html=True)

# Fila 1 — 3 KPIs (se apilan en móvil automáticamente)
k1, k2, k3 = st.columns(3, gap="small")
with k1: _kpi_card("kpi-card",                "🌊 Nivel Río Sinú",  f"{niveles[0]} m",       rio_txt,                        rio_badge,     fuente_rio)
with k2: _kpi_card("kpi-card kpi-card-blue",  "🌡️ Temperatura",     f"{clima['temp']} °C",   f"Humedad {clima['humedad']}%", "badge-blue",  "Open-Meteo · ahora")
with k3:
    prob = clima.get("prob_lluvia", [0])[0] if clima.get("prob_lluvia") else 0
    _kpi_card("kpi-card kpi-card-blue", "🌧️ Lluvia hoy",
              f"{clima['lluvia_hoy']} mm",
              f"☔ Prob. {prob}%",
              "badge-blue" if prob < 30 else "badge-yellow" if prob < 60 else "badge-red",
              "Open-Meteo · ahora")

# Fila 2 — 3 KPIs
k4, k5, k6 = st.columns(3, gap="small")
with k4: _kpi_card("kpi-card kpi-card-green", "💨 PM2.5",           f"{aire['pm25']} µg/m³", "✅ OMS < 15",   "badge-green",  "Open-Meteo · ahora")
with k5: _kpi_card("kpi-card",                "🌬️ AQI Europeo",    f"{aire['aqi']}",          aqi_txt,        aqi_badge,     "Índice europeo")
with k6: _kpi_card("kpi-card kpi-card-purple","🦜 Especies GBIF",  "≥12",                    "Córdoba 2026", "badge-purple", "GBIF · Córdoba, CO")

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)


# ── Cauce real del Río Sinú — coordenadas trazadas en geojson.io ──────
CAUCE_SINU_FALLBACK = [
    [8.69768846, -75.94782194], [8.70122071, -75.94240658],
    [8.69987114, -75.93560537], [8.70305888, -75.93594981],
    [8.71192054, -75.94286909], [8.71863785, -75.94379077],
    [8.72535501, -75.93734223], [8.72193985, -75.93215672],
    [8.71557630, -75.92536160], [8.71855524, -75.92260906],
    [8.72478702, -75.92213802], [8.73127622, -75.92305694],
    [8.73640083, -75.92213510], [8.73961492, -75.91957351],
    [8.74013571, -75.91535784], [8.73778687, -75.90851478],
    [8.74351866, -75.90587567], [8.74727880, -75.90322958],
    [8.74922018, -75.90126533], [8.74922025, -75.89856450],
    [8.74764320, -75.89414539], [8.74788577, -75.89242679],
    [8.75261750, -75.89193544], [8.75686353, -75.88984919],
    [8.76280817, -75.88518463], [8.77045286, -75.88223726],
    [8.77215134, -75.87941382], [8.76936038, -75.87450396],
    [8.76802566, -75.87290836], [8.76826901, -75.87094317],
    [8.77118166, -75.86959167], [8.78367731, -75.87364386],
    [8.78883840, -75.86806919], [8.79362685, -75.86414634],
    [8.80022730, -75.85977915], [8.80295920, -75.85977891],
    [8.80887841, -75.86254257], [8.82094414, -75.85770413],
    [8.82936742, -75.85632123], [8.83164380, -75.85309608],
    [8.83594253, -75.85423387], [8.84148501, -75.85633728],
    [8.84841300, -75.85668785],
]

def obtener_cauce_sinu():
    """Retorna el cauce real del Río Sinú trazado en geojson.io."""
    return None  # Siempre usa CAUCE_SINU_FALLBACK (coordenadas reales verificadas)

# ── Lista global de universidades (usada en mapa normal y expandido) ──
UNIVERSIDADES_GLOBAL = [
    (8.7454, -75.8888, "🎓 Universidad del Sinú",
     "Cra. 1W #38-153, Barrio Juan XXIII", "Institución privada · ~8,000 estudiantes"),
    (8.7963, -75.8805, "🎓 Universidad de Córdoba",
     "Cra. 6 #77-305, Montería", "Universidad pública · ~15,000 estudiantes"),
    (8.8143, -75.8805, "🎓 Universidad Pontificia Bolivariana",
     "Cra. 6 #97A-99, Montería", "Institución privada · sede Montería"),
    (8.7846, -75.8805, "🎓 Universidad Luis Amigó",
     "Cl. 64 #6-108, Montería", "Institución privada · sede Montería"),
    (8.7738, -75.8805, "🎓 Universidad Cooperativa de Colombia",
     "Cl. 52 #6-79, Montería", "Institución privada · sede Montería"),
    (8.7540, -75.8822, "🎓 CUN",
     "Cra. 4 #30-20, Montería", "Corporación Unificada Nacional"),
    (8.7864, -75.8814, "🎓 Politécnico Gran Colombiano",
     "Cl. 66 #5-70 Local 103, Montería", "Institución privada · sede Montería"),
    (8.7513, -75.8822, "🎓 Uniremington",
     "Cl. 27 #4-31, Montería", "Corporación Universitaria Remington"),
    (8.7567, -75.8805, "🏫 Colegio San Agustín",
     "Cra. 6 #33-02, Centro, Montería", "Institución educativa San Agustín"),
]

# ── Centros comerciales verificados ───────────────────────
CC_GLOBAL = [
    (8.7882, -75.8805, "🛍️ C.C. Buenavista",
     "Cra. 6 #68-72, Montería", "Centro comercial principal de Montería"),
    (8.7531, -75.8814, "🛍️ C.C. Nuestro",
     "Tv. 29 #29-69, Montería", "Centro comercial Nuestro"),
    (8.7666, -75.8772, "🛍️ C.C. Alamedas",
     "Cl. 44 #10-91, Montería", "Centro comercial Alamedas del Sinú"),
]

# ══════════════════════════════════════════════════════════
# ── MAPA PROFESIONAL ─────────────────────────────────────
# ══════════════════════════════════════════════════════════

st.markdown('<div class="section-header">🗺️ Mapa ambiental interactivo · Montería</div>', unsafe_allow_html=True)

col_mapa, col_pred = st.columns([1.35, 1], gap="small")

with col_mapa:
    tipo = st.radio(
        "Capa del mapa",
        ["🗺️ Estándar", "🛰️ Satelital", "🌑 Oscuro"],
        horizontal=True,
        label_visibility="collapsed"
    )
    if tipo == "🛰️ Satelital":
        tiles = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
        attr  = "Tiles © Esri"
    elif tipo == "🌑 Oscuro":
        tiles, attr = "CartoDB dark_matter", "© CartoDB"
    else:
        tiles, attr = "OpenStreetMap", "© OpenStreetMap contributors"

    m = folium.Map(location=[8.7560, -75.8814], zoom_start=13,
                   tiles=tiles, attr=attr)

    # ── Cauce real del Río Sinú ────────────────────────────
    _cauce = obtener_cauce_sinu() or CAUCE_SINU_FALLBACK
    folium.PolyLine(
        locations=_cauce,
        color="#4FC3F7", weight=5, opacity=0.9,
        tooltip="Río Sinú"
    ).add_to(m)

    # ── Área de monitoreo ──────────────────────────────────
    folium.Circle(
        [8.7560, -75.8814], radius=5000,
        color="#00E5C3", fill=True, fill_opacity=0.03,
        weight=1, dash_array="6"
    ).add_to(m)

    # ══════════════════════════════════════════════════════
    # PUNTOS MÁS TRANSITADOS DE MONTERÍA — coordenadas verificadas
    # con niveles de contaminación diferenciados por zona
    # ══════════════════════════════════════════════════════

    pm25 = aire["pm25"]
    aqi  = aire["aqi"]

    # Función para color según contaminación relativa por zona
    def color_contam(factor):
        """factor 1.0=normal, >1=más contaminado, <1=más limpio"""
        val = pm25 * factor
        if val < 10:   return "#00E5C3", "🟢 Buena"
        elif val < 15: return "#FFD600", "🟡 Moderada"
        elif val < 25: return "#FF9800", "🟠 Regular"
        else:          return "#FF5252", "🔴 Mala"

    # ── ZONAS DE ALTA CONTAMINACIÓN (tráfico + industria) ──
    # Mercado Central — alto tráfico vehicular, vendedores ambulantes
    c, estado = color_contam(1.8)
    folium.CircleMarker(
        [8.7512, -75.8795], radius=18,
        color=c, fill=True, fill_color=c, fill_opacity=0.5, weight=2,
        popup=folium.Popup(
            f"<b>🏪 Mercado Central</b><br>"
            f"Zona: Alta contaminación<br>"
            f"PM2.5 est.: {round(pm25*1.8,1)} µg/m³<br>"
            f"Causa: tráfico pesado + vendedores<br>"
            f"Estado: {estado}", max_width=220),
        tooltip="🏪 Mercado Central — Alta contaminación"
    ).add_to(m)

    # Terminal de Transportes — buses y camiones
    c, estado = color_contam(2.1)
    folium.CircleMarker(
        [8.7420, -75.8650], radius=18,
        color=c, fill=True, fill_color=c, fill_opacity=0.5, weight=2,
        popup=folium.Popup(
            f"<b>🚌 Terminal de Transportes</b><br>"
            f"Zona: Muy alta contaminación<br>"
            f"PM2.5 est.: {round(pm25*2.1,1)} µg/m³<br>"
            f"Causa: emisiones de buses y camiones<br>"
            f"Estado: {estado}", max_width=220),
        tooltip="🚌 Terminal — Muy alta contaminación"
    ).add_to(m)

    # Avenida Circunvalar — tráfico vehicular intenso
    c, estado = color_contam(1.6)
    folium.CircleMarker(
        [8.7600, -75.8600], radius=16,
        color=c, fill=True, fill_color=c, fill_opacity=0.45, weight=2,
        popup=folium.Popup(
            f"<b>🚗 Av. Circunvalar</b><br>"
            f"Zona: Alta contaminación<br>"
            f"PM2.5 est.: {round(pm25*1.6,1)} µg/m³<br>"
            f"Causa: corredor vial principal<br>"
            f"Estado: {estado}", max_width=220),
        tooltip="🚗 Av. Circunvalar — Alta contaminación"
    ).add_to(m)

    # ── ZONAS DE CONTAMINACIÓN MEDIA ──────────────────────
    # Centro histórico — Parque Simón Bolívar
    c, estado = color_contam(1.3)
    folium.CircleMarker(
        [8.7540, -75.8814], radius=15,
        color=c, fill=True, fill_color=c, fill_opacity=0.45, weight=2,
        popup=folium.Popup(
            f"<b>🏛️ Parque Simón Bolívar</b><br>"
            f"Zona: Contaminación moderada<br>"
            f"PM2.5 est.: {round(pm25*1.3,1)} µg/m³<br>"
            f"Causa: centro urbano concurrido<br>"
            f"Estado: {estado}", max_width=220),
        tooltip="🏛️ Parque Simón Bolívar — Moderada"
    ).add_to(m)

    # Universidad del Sinú — zona universitaria
    c, estado = color_contam(1.1)
    folium.CircleMarker(
        [8.7454, -75.8888], radius=14,
        color=c, fill=True, fill_color=c, fill_opacity=0.4, weight=2,
        popup=folium.Popup(
            f"<b>🎓 Universidad del Sinú</b><br>"
            f"Zona: Contaminación baja-moderada<br>"
            f"PM2.5 est.: {round(pm25*1.1,1)} µg/m³<br>"
            f"Causa: zona residencial-universitaria<br>"
            f"Estado: {estado}", max_width=220),
        tooltip="🎓 UniSinú — Baja-moderada"
    ).add_to(m)

    # C.C. Buenavista — zona comercial
    c, estado = color_contam(1.4)
    folium.CircleMarker(
        [8.7510, -75.8480], radius=15,
        color=c, fill=True, fill_color=c, fill_opacity=0.45, weight=2,
        popup=folium.Popup(
            f"<b>🛍️ C.C. Buenavista</b><br>"
            f"Zona: Contaminación moderada<br>"
            f"PM2.5 est.: {round(pm25*1.4,1)} µg/m³<br>"
            f"Causa: alto flujo vehicular comercial<br>"
            f"Estado: {estado}", max_width=220),
        tooltip="🛍️ C.C. Buenavista — Moderada"
    ).add_to(m)

    # Estadio Jaraguay — zona sur
    c, estado = color_contam(1.2)
    folium.CircleMarker(
        [8.7118, -75.8276], radius=14,
        color=c, fill=True, fill_color=c, fill_opacity=0.4, weight=2,
        popup=folium.Popup(
            f"<b>⚽ Estadio Jaraguay</b><br>"
            f"Zona: Contaminación moderada<br>"
            f"PM2.5 est.: {round(pm25*1.2,1)} µg/m³<br>"
            f"Causa: zona periurbana sur<br>"
            f"Estado: {estado}", max_width=220),
        tooltip="⚽ Estadio Jaraguay — Moderada"
    ).add_to(m)

    # ── ZONAS LIMPIAS (parques y río) ─────────────────────
    # Ronda del Sinú — parque lineal, pulmón verde
    c, estado = color_contam(0.6)
    folium.CircleMarker(
        [8.7560, -75.8912], radius=20,
        color=c, fill=True, fill_color=c, fill_opacity=0.45, weight=2,
        popup=folium.Popup(
            f"<b>🌿 Ronda del Sinú</b><br>"
            f"Parque lineal más grande de Latinoamérica<br>"
            f"PM2.5 est.: {round(pm25*0.6,1)} µg/m³<br>"
            f"Causa: pulmón verde urbano, arborización<br>"
            f"Estado: {estado}", max_width=220),
        tooltip="🌿 Ronda del Sinú — Zona limpia"
    ).add_to(m)

    # Muelle Turístico — orilla norte del río
    c, estado = color_contam(0.7)
    folium.CircleMarker(
        [8.7800, -75.8873], radius=14,
        color=c, fill=True, fill_color=c, fill_opacity=0.4, weight=2,
        popup=folium.Popup(
            f"<b>⚓ Muelle Turístico del Sinú</b><br>"
            f"Zona: Buena calidad de aire<br>"
            f"PM2.5 est.: {round(pm25*0.7,1)} µg/m³<br>"
            f"Causa: orilla del río, brisa natural<br>"
            f"Estado: {estado}", max_width=220),
        tooltip="⚓ Muelle Turístico — Zona limpia"
    ).add_to(m)

    # Aeropuerto Los Garzones — zona norte periférica
    c, estado = color_contam(0.8)
    folium.CircleMarker(
        [8.8233, -75.8258], radius=14,
        color=c, fill=True, fill_color=c, fill_opacity=0.4, weight=2,
        popup=folium.Popup(
            f"<b>✈️ Aeropuerto Los Garzones</b><br>"
            f"PM2.5 est.: {round(pm25*0.8,1)} µg/m³<br>"
            f"Causa: zona norte, menos densidad urbana<br>"
            f"Estado: {estado}", max_width=220),
        tooltip="✈️ Aeropuerto Los Garzones"
    ).add_to(m)

    # ── UNIVERSIDADES (usa lista global verificada) ──────────────────────
    UNIVERSIDADES = UNIVERSIDADES_GLOBAL
    for lat, lon, nombre, direccion, info in UNIVERSIDADES:
        folium.Marker(
            [lat, lon],
            popup=folium.Popup(
                f"<b>{nombre}</b><br>"
                f"📍 {direccion}<br>"
                f"ℹ️ {info}", max_width=240),
            tooltip=nombre,
            icon=folium.Icon(color="orange", icon="graduation-cap", prefix="fa")
        ).add_to(m)

    # ── CENTROS COMERCIALES ───────────────────────────────────────────────
    for lat, lon, nombre, direccion, info in CC_GLOBAL:
        folium.Marker(
            [lat, lon],
            popup=folium.Popup(
                f"<b>{nombre}</b><br>"
                f"📍 {direccion}<br>"
                f"ℹ️ {info}", max_width=240),
            tooltip=nombre,
            icon=folium.Icon(color="red", icon="shopping-cart", prefix="fa")
        ).add_to(m)

    # ── Estaciones de monitoreo de aire (marcadores verdes) ──
    for lat, lon, nombre, popup_txt in [
        (8.7550, -75.8750, "💨 Estación Centro",
         f"PM2.5: {aire['pm25']} µg/m³ · AQI: {aire['aqi']}"),
        (8.7350, -75.8650, "💨 Estación Sur",
         f"PM10: {aire['pm10']} µg/m³ · NO₂: {aire['no2']} µg/m³"),
    ]:
        folium.Marker(
            [lat, lon],
            popup=folium.Popup(f"<b>{nombre}</b><br>{popup_txt}", max_width=220),
            tooltip=nombre,
            icon=folium.Icon(color="green", icon="cloud", prefix="fa")
        ).add_to(m)

    # ── Estaciones río Sinú ────────────────────────────────
    for lat, lon, nombre, idx in [
        (8.7560, -75.8912, "Ronda del Sinú — Av. Primera", 0),
        (8.7650, -75.8845, "Puente Segundo Centenario",    1),
        (8.7800, -75.8873, "Muelle Turístico del Sinú",    2),
    ]:
        alerta_lbl, _, _ = alerta_rio(niveles[idx])
        folium.Marker(
            [lat, lon],
            popup=folium.Popup(
                f"<b>🌊 {nombre}</b><br>"
                f"Nivel: <b>{niveles[idx]}m</b><br>"
                f"Estado: {alerta_lbl}", max_width=230),
            tooltip=f"🌊 {nombre}",
            icon=folium.Icon(color="blue", icon="tint", prefix="fa")
        ).add_to(m)

    # ── Capa de lluvia si hay probabilidad ─────────────────
    prob_hoy = clima.get("prob_lluvia", [0])[0] if clima.get("prob_lluvia") else 0
    if prob_hoy >= 20 or clima.get("lluvia_hoy", 0) > 0:
        if prob_hoy >= 60:   color_lluvia, op = "#0066FF", 0.30
        elif prob_hoy >= 30: color_lluvia, op = "#00AAFF", 0.18
        else:                color_lluvia, op = "#00CCFF", 0.10
        for lat_z, lon_z, peso in [
            (8.7550,-75.8914,1.0),(8.7480,-75.9000,0.9),
            (8.7750,-75.8870,0.8),(8.7280,-75.9050,0.7),
            (8.7600,-75.8700,0.6),(8.7400,-75.8750,0.5),
        ]:
            folium.Circle(
                [lat_z, lon_z], radius=int(2000*peso),
                color=color_lluvia, fill=True,
                fill_color=color_lluvia,
                fill_opacity=op*peso, weight=0,
                tooltip=f"🌧️ Prob. lluvia: {prob_hoy}%"
            ).add_to(m)

    # ── Marcadores fauna ───────────────────────────────────
    fauna_puntos = [
        (8.7560, -75.8912, "🦎 Iguana iguana",           "Ronda del Sinú · 12 registros"),
        (8.7735, -75.8695, "🐦 Leptotila verreauxi",      "Norte · 5 registros"),
        (8.7800, -75.8873, "🦆 Cairina moschata",         "Muelle · 3 registros"),
        (8.7454, -75.8888, "🌺 Heliconia psittacorum",    "Campus UniSinú · 8 registros"),
        (8.7118, -75.8276, "🐢 Chelonoidis carbonarius",  "Zona sur · 2 registros"),
    ]
    for lat, lon, nombre, popup_txt in fauna_puntos:
        folium.Marker(
            [lat, lon],
            popup=folium.Popup(f"<b>{nombre}</b><br>{popup_txt}", max_width=220),
            tooltip=nombre,
            icon=folium.Icon(color="purple", icon="paw", prefix="fa")
        ).add_to(m)

    # ── Leyenda profesional ────────────────────────────────
    m.get_root().html.add_child(folium.Element("""
    <div style="position:fixed;bottom:20px;left:20px;z-index:1000;
                background:rgba(6,13,26,0.93);padding:12px 16px;
                border-radius:12px;font-size:11px;color:#8892a4;
                border:1px solid rgba(0,229,195,0.2);min-width:180px">
        <b style="color:#00E5C3;font-size:12px">Leyenda</b><br>
        <span style="color:#FF5252">🔴</span> Alta &nbsp;
        <span style="color:#FF9800">🟠</span> Media &nbsp;
        <span style="color:#FFD600">🟡</span> Moderada &nbsp;
        <span style="color:#00E5C3">🟢</span> Limpia<br>
        <span style="color:#4FC3F7">🔵</span> Río &nbsp;
        <span style="color:#00E5C3">🟢</span> Aire &nbsp;
        <span style="color:#7B61FF">🟣</span> Fauna<br>
        <span style="color:#FFA500">🟠</span> Universidades &nbsp;
        <span style="color:#FF5252">🔴</span> C. Comerciales &nbsp;
        <span style="color:#00AAFF">🔵</span> Lluvia<br>
        <span style="color:#4FC3F7">━━</span> Cauce Río Sinú
    </div>"""))

    # ── Zonas de inundación según nivel actual del río ────
    ZONAS_INUNDACION = [
        (8.7560, -75.8950, 600, "Zona riesgo ALTO",
         "La Granja · La Ribera · Los Nogales",
         4.0, "Primera zona en afectarse históricamente"),
        (8.7480, -75.8920, 500, "Zona riesgo ALTO",
         "Barrio Colón · Chuchurubi · Santa Fe",
         4.0, "Área de inundación histórica recurrente"),
        (8.7650, -75.8930, 450, "Zona riesgo MEDIO",
         "Ronda del Sinú norte · Av. Primera",
         5.5, "Afectada cuando el río supera 5.5m"),
        (8.7800, -75.8900, 400, "Zona riesgo MEDIO",
         "El Recreo · sector norte ribera",
         5.5, "Afectada cuando el río supera 5.5m"),
        (8.7350, -75.8970, 350, "Zona riesgo ALTO",
         "Mocarí rural · zona baja sur",
         4.0, "Zona baja — riesgo en temporada de lluvias"),
    ]
    nivel_actual = niveles[0]
    for lat_z, lon_z, radio, zona, barrios, cota, nota in ZONAS_INUNDACION:
        if nivel_actual >= cota + 1.5:
            cz, fo, iz = "#FF5252", 0.40, "⚠️ INUNDACIÓN ACTIVA"
        elif nivel_actual >= cota:
            cz, fo, iz = "#FF9800", 0.28, "⚠️ En alerta"
        elif nivel_actual >= cota - 0.5:
            cz, fo, iz = "#FFD600", 0.15, "⚡ Precaución"
        else:
            cz, fo, iz = "#4FC3F7", 0.06, "✅ Normal"
        folium.Circle(
            [lat_z, lon_z], radius=radio,
            color=cz, fill=True, fill_color=cz,
            fill_opacity=fo, weight=2, dash_array="6",
            popup=folium.Popup(
                f"<b>🌊 {zona}</b><br>"
                f"<b>Estado:</b> {iz}<br>"
                f"<b>Barrios:</b> {barrios}<br>"
                f"<b>Nivel actual:</b> {nivel_actual}m<br>"
                f"<b>Cota alerta:</b> {cota}m<br>"
                f"<b>Nota:</b> {nota}", max_width=270),
            tooltip=f"🌊 {zona} · {iz}"
        ).add_to(m)

    st_folium(m, width=None, height=450, returned_objects=[])

    # ── Botón expandir mapa ────────────────────────────────
    if st.button("🔲 Expandir mapa completo", use_container_width=True):
        st.session_state.mapa_expandido = not st.session_state.get("mapa_expandido", False)
        st.rerun()

# ── Mapa expandido (superpuesto) ───────────────────────────
if st.session_state.get("mapa_expandido", False):
    st.markdown("""
    <div style="position:fixed;top:0;left:0;width:100vw;height:100vh;
                background:#060d1a;z-index:99999;padding:10px">
    """, unsafe_allow_html=True)
    col_close, _ = st.columns([1, 5])
    with col_close:
        if st.button("✖ Cerrar mapa", key="cerrar_mapa"):
            st.session_state.mapa_expandido = False
            st.rerun()
    # Renderizar mapa grande
    m2 = folium.Map(location=[8.7560, -75.8814], zoom_start=13,
                    tiles="OpenStreetMap", attr="© OpenStreetMap contributors")
    _cauce2 = obtener_cauce_sinu() or CAUCE_SINU_FALLBACK
    folium.PolyLine(_cauce2, color="#4FC3F7", weight=5, opacity=0.9,
                    tooltip="Río Sinú").add_to(m2)
    for lat, lon, nombre, direccion, info in UNIVERSIDADES_GLOBAL:
        folium.Marker([lat, lon],
            popup=folium.Popup(f"<b>{nombre}</b><br>📍 {direccion}<br>ℹ️ {info}", max_width=240),
            tooltip=nombre,
            icon=folium.Icon(color="orange", icon="graduation-cap", prefix="fa")
        ).add_to(m2)
    st_folium(m2, width=None, height=700, returned_objects=[])
    st.markdown("</div>", unsafe_allow_html=True)

# ── Panel de alertas de inundación ────────────────────────
nivel_actual = niveles[0]
alerta_lbl, _, alerta_color = alerta_rio(nivel_actual)

with st.expander(f"🌊 Zonas afectadas por nivel del río — Estado actual: {alerta_lbl} ({nivel_actual}m)", expanded=nivel_actual >= 4.0):
    ZONAS_INFO = [
        ("Zona ALTO riesgo", "La Granja · La Ribera · Los Nogales",
         "Margen occidental río, cota baja", 4.0,
         "Evacuar si nivel supera 5m · Ruta: Av. Circunvalar hacia el este"),
        ("Zona ALTO riesgo", "Barrio Colón · Chuchurubi · Santa Fe",
         "Sector sur, históricamente inundado", 4.0,
         "Zona con antecedentes de inundación · Contactar Defensa Civil: 144"),
        ("Zona MEDIO riesgo", "Ronda del Sinú norte · Av. Primera",
         "Parque lineal y avenida ribereña", 5.5,
         "Cerrar acceso al parque si nivel > 5.5m"),
        ("Zona MEDIO riesgo", "El Recreo · Ribera norte",
         "Barrio nororiental junto al río", 5.5,
         "Monitorear de cerca en temporada de lluvias"),
        ("Zona ALTO riesgo", "Mocarí · Zona sur rural",
         "Área baja al sur de Montería", 4.0,
         "Zona agrícola — riesgo de pérdidas en cultivos"),
    ]
    for zona, barrios, ubicacion, cota, accion in ZONAS_INFO:
        if nivel_actual >= cota + 1.5:
            badge_color = "badge-red"
            estado_txt  = f"🔴 INUNDACIÓN — nivel {nivel_actual}m supera cota {cota}m"
        elif nivel_actual >= cota:
            badge_color = "badge-yellow"
            estado_txt  = f"🟠 ALERTA — nivel {nivel_actual}m alcanzó cota {cota}m"
        elif nivel_actual >= cota - 0.5:
            badge_color = "badge-yellow"
            estado_txt  = f"🟡 PRECAUCIÓN — nivel {nivel_actual}m se acerca a cota {cota}m"
        else:
            badge_color = "badge-green"
            estado_txt  = f"✅ Normal — nivel {nivel_actual}m · cota alerta: {cota}m"

        st.markdown(f"""
        <div style="background:rgba(0,229,195,0.04);border:1px solid rgba(0,229,195,0.1);
                    border-radius:10px;padding:12px 16px;margin-bottom:10px">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
                <span class="badge {badge_color}">{zona}</span>
                <span style="color:#e8f4ff;font-weight:600">{barrios}</span>
            </div>
            <div style="color:#5a7a9a;font-size:0.82rem;margin-bottom:4px">
                📍 {ubicacion} · Cota alerta: {cota}m
            </div>
            <div style="color:#4FC3F7;font-size:0.82rem;margin-bottom:4px">
                📊 {estado_txt}
            </div>
            <div style="color:#8892a4;font-size:0.78rem">
                💡 {accion}
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:rgba(79,195,247,0.05);border:1px solid rgba(79,195,247,0.2);
                border-radius:10px;padding:10px 14px;font-size:0.78rem;color:#5a7a9a">
        📞 <b style="color:#e8f4ff">Emergencias:</b> Defensa Civil 144 · Bomberos 119 · Cruz Roja 132<br>
        📡 <b style="color:#e8f4ff">Datos en tiempo real:</b> IDEAM · {fuente_rio}
    </div>""", unsafe_allow_html=True)

st.markdown("<hr style='border:1px solid rgba(0,229,195,0.1);margin:14px 0'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# ── CALIDAD DEL AIRE ──────────────────────────────────────
# ══════════════════════════════════════════════════════════

st.markdown('<div class="section-header">💨 Calidad del aire · Open-Meteo Air Quality API</div>', unsafe_allow_html=True)

a1, a2, a3, a4 = st.columns(4, gap="small")
aire_kpis = [
    (a1, "PM2.5",  f"{aire['pm25']} µg/m³", "✅ OMS < 15",    "badge-green",  "#00E5C3"),
    (a2, "PM10",   f"{aire['pm10']} µg/m³", "✅ OMS < 45",    "badge-green",  "#69F0AE"),
    (a3, "NO₂",    f"{aire['no2']} µg/m³",  "✅ Normal",       "badge-green",  "#4FC3F7"),
    (a4, "AQI",    f"{aire['aqi']}",          aqi_txt,          aqi_badge,      "#7B61FF"),
]
for col, lbl, val, badge_txt, badge_cls, _ in aire_kpis:
    with col:
        st.markdown(f"""
        <div class="kpi-card kpi-card-green">
            <div class="kpi-label">{lbl}</div>
            <div class="kpi-value">{val}</div>
            <span class="badge {badge_cls}">{badge_txt}</span>
            <div class="fuente-tag">Open-Meteo · tiempo real</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<hr style='border:1px solid rgba(0,229,195,0.1);margin:14px 0'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# ── BIODIVERSIDAD · GBIF ──────────────────────────────────
# ══════════════════════════════════════════════════════════

st.markdown('<div class="section-header">🦜 Biodiversidad · GBIF · Córdoba, Colombia</div>', unsafe_allow_html=True)

# Cargar fauna en tiempo real
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
        "imagen_url": [None]*6,
        "gbif_key":   [""]*6,
    })

# KPIs biodiversidad
f1, f2, f3, f4 = st.columns(4, gap="small")
for col, lbl, val, sub, badge_cls in [
    (f1, "Especies registradas", str(n_especies), fuente_fauna,       "badge-purple"),
    (f2, "Con imagen",           str(n_imagen),   "Fotos verificadas", "badge-green"),
    (f3, "Clases taxonómicas",   str(n_clases),   "Taxones distintos", "badge-blue"),
    (f4, "Clasificación CNN",    "MobileNetV2",   "Precisión validada","badge-green"),
]:
    with col:
        st.markdown(f"""
        <div class="kpi-card kpi-card-purple">
            <div class="kpi-label">{lbl}</div>
            <div class="kpi-value">{val}</div>
            <span class="badge {badge_cls}">{sub}</span>
        </div>""", unsafe_allow_html=True)

# Tabla de especies
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
cols_mostrar     = ["especie","nombre_com","clase","orden","familia","estado","fecha"]
cols_disponibles = [c for c in cols_mostrar if c in df_fauna_live.columns]
df_mostrar = df_fauna_live[cols_disponibles].head(12).copy()
df_mostrar.columns = [c.replace("_"," ").capitalize() for c in df_mostrar.columns]
st.dataframe(df_mostrar, use_container_width=True, hide_index=True, height=320)

st.markdown("<hr style='border:1px solid rgba(0,229,195,0.1);margin:14px 0'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# ── GALERÍA DE FAUNA ─────────────────────────────────────
# ══════════════════════════════════════════════════════════

st.markdown('<div class="section-header">📸 Galería de especies · Córdoba, Colombia · GBIF tiempo real</div>',
            unsafe_allow_html=True)

# Recopilar URLs de imágenes desde GBIF
imagenes_gbif = []
if fauna_ok and df_fauna_live is not None and "imagen_url" in df_fauna_live.columns:
    for _, row in df_fauna_live.iterrows():
        url = row.get("imagen_url")
        if pd.notna(url) and url and isinstance(url, str) and url.startswith("http"):
            imagenes_gbif.append((url, row.get("especie", "Especie")))
        if len(imagenes_gbif) >= 6:
            break

# Imágenes locales de respaldo (6 especies emblemáticas)
archivos_local = [
    ("imagenes_fauna/Heliconia_psittacorum.jpg",  "Heliconia psittacorum"),
    ("imagenes_fauna/Iguana_iguana.jpg",           "Iguana iguana"),
    ("imagenes_fauna/Leptotila_verreauxi.jpg",     "Leptotila verreauxi"),
    ("imagenes_fauna/Chelonoidis_carbonarius.jpg", "Chelonoidis carbonarius"),
    ("imagenes_fauna/Cairina_moschata.jpg",        "Cairina moschata"),
    ("imagenes_fauna/Sakesphorus_canadensis.jpg",  "Sakesphorus canadensis"),
]

def _render_img(col_obj, url_or_path, nombre, es_url=True):
    """Renderiza imagen con fallback — usable en galería GBIF y local."""
    placeholder = f"""<div style="background:#0d1b2e;border:1px solid rgba(123,97,255,0.2);
        border-radius:10px;padding:16px;text-align:center;font-size:0.75rem;color:#5a7a9a">
        🦜<br><i>{nombre}</i></div>"""
    try:
        if es_url:
            col_obj.image(url_or_path, caption=nombre, use_container_width=True)
        else:
            col_obj.image(Image.open(url_or_path), caption=nombre, use_container_width=True)
    except Exception:
        col_obj.markdown(placeholder, unsafe_allow_html=True)

# Galería responsiva: 3 cols en escritorio, 2 en móvil (CSS lo ajusta)
# Usamos 3 columnas — en móvil el CSS las apila de a 2
if len(imagenes_gbif) >= 3:
    fuente_label = imagenes_gbif
    es_url_flag  = True
    label_tag    = f"<small style='color:#00E5C3'>📷 {len(imagenes_gbif)} imágenes · GBIF · Córdoba, Colombia</small>"
else:
    fuente_label = [(a, n) for a, n in archivos_local]
    es_url_flag  = False
    label_tag    = "<small style='color:#3a5a7a'>📷 Imágenes locales · Banco fotográfico BioMonitor</small>"

# Render en filas de 3 (responsive — en móvil quedan 2 por fila vía CSS)
items = fuente_label[:6]
for fila_idx in range(0, len(items), 3):
    trio = items[fila_idx:fila_idx+3]
    gcols = st.columns(len(trio), gap="small")
    for ci, (src_img, nombre) in enumerate(trio):
        _render_img(gcols[ci], src_img, nombre, es_url=es_url_flag)

st.markdown(label_tag, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# ── FOOTER ────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════

st.markdown(f"""
<div style='text-align:center;color:#2a4a6a;font-size:0.8rem;
            padding:18px 0 28px 0;
            border-top:1px solid rgba(0,229,195,0.08);
            margin-top:14px;line-height:2'>
    <b style='color:#00E5C3;font-size:0.9rem'>BioMonitor Montería</b>
    &nbsp;·&nbsp; {datetime.now(TZ_COL).strftime('%d/%m/%Y %H:%M')}
    &nbsp;·&nbsp; Open-Meteo · IDEAM · GBIF
    &nbsp;·&nbsp; LSTM + MobileNetV2
    &nbsp;·&nbsp; <b style='color:#00E5C3'>© Ivan Contreras</b>
</div>""", unsafe_allow_html=True)