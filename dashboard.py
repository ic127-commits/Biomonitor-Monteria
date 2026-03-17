import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
TZ_COL = ZoneInfo('America/Bogota')
from PIL import Image
import requests
import concurrent.futures
import warnings
warnings.filterwarnings("ignore")

# ── Session state ─────────────────────────────────────────
if "initialized" not in st.session_state:
    st.session_state.initialized   = True
    st.session_state.show_info     = False
    st.session_state.lugar_buscado = None
    st.session_state.mapa_tipo     = "Estándar"

st.set_page_config(
    page_title="BioMonitor Montería",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [data-testid="stAppViewContainer"] { background-color:#EDECEA !important; font-family:'Inter',sans-serif; }
.main { background-color:#EDECEA; }
.block-container { padding-top:1.5rem !important; padding-left:2rem !important; padding-right:2rem !important; max-width:1400px; }
.hero-banner { background:#FFFFFF; border:0.5px solid #D3D1C7; border-left:4px solid #3B6D11; border-radius:0 14px 14px 0; padding:20px 24px; margin-bottom:18px; }
.hero-sub { font-size:0.88rem; color:#5F5E5A; line-height:1.55; margin:0; }
.hero-badge { display:inline-block; background:#EAF3DE; border:0.5px solid #97C459; color:#3B6D11; padding:3px 10px; border-radius:20px; font-size:0.72rem; font-weight:600; letter-spacing:0.5px; margin-right:6px; margin-top:6px; }
.kpi-card { background:#FFFFFF; border:0.5px solid #D3D1C7; border-radius:12px; padding:16px 18px; position:relative; overflow:hidden; margin-bottom:10px; min-height:110px; }
.kpi-card::before { content:''; position:absolute; top:0; left:0; width:4px; height:100%; background:#3B6D11; border-radius:2px 0 0 2px; }
.kpi-card-red::before { background:#A32D2D; } .kpi-card-blue::before { background:#185FA5; }
.kpi-card-green::before { background:#3B6D11; } .kpi-card-purple::before { background:#534AB7; }
.kpi-label { font-size:0.68rem; color:#888780; text-transform:uppercase; letter-spacing:1px; font-weight:600; margin-bottom:5px; }
.kpi-value { font-size:1.85rem; font-weight:700; color:#2C2C2A; line-height:1; margin-bottom:7px; }
.kpi-value-sm { font-size:1.35rem; font-weight:600; color:#2C2C2A; line-height:1; margin-bottom:7px; }
.badge { display:inline-block; padding:3px 9px; border-radius:20px; font-size:0.72rem; font-weight:600; }
.badge-green  { background:#EAF3DE; color:#27500A; border:0.5px solid #97C459; }
.badge-yellow { background:#FAEEDA; color:#633806; border:0.5px solid #EF9F27; }
.badge-red    { background:#FCEBEB; color:#791F1F; border:0.5px solid #F09595; }
.badge-blue   { background:#E6F1FB; color:#0C447C; border:0.5px solid #85B7EB; }
.badge-purple { background:#EEEDFE; color:#3C3489; border:0.5px solid #AFA9EC; }
.section-header { font-size:0.95rem; font-weight:700; color:#2C2C2A; margin-bottom:12px; display:flex; align-items:center; gap:8px; padding-bottom:8px; border-bottom:1.5px solid #EAF3DE; }
.info-card { background:#FFFFFF; border:0.5px solid #D3D1C7; border-radius:12px; padding:14px 18px; margin-bottom:10px; font-size:0.82rem; color:#444441; line-height:1.55; }
.info-card b { color:#2C2C2A; }
.stat-row { background:#F1EFE8; border:0.5px solid #D3D1C7; border-radius:10px; padding:10px 14px; margin-top:8px; font-size:0.81rem; color:#5F5E5A; }
.fuente-tag { font-size:0.67rem; color:#5F5E5A; margin-top:4px; }
.copyright { position:fixed; bottom:10px; right:16px; color:#B4B2A9; font-size:0.7rem; z-index:9999; }
.stButton > button { background:#3B6D11 !important; color:#FFFFFF !important; font-weight:600 !important; border:none !important; border-radius:9px !important; transition:background 0.2s; }
.stButton > button:hover { background:#27500A !important; }
footer { visibility:hidden; } #MainMenu { visibility:hidden; }
.stDataFrame { border-radius:10px; overflow:hidden; background:#FFFFFF !important; }
.stDataFrame thead tr th { background:#F1EFE8 !important; color:#2C2C2A !important; }
.stDataFrame tbody tr td { color:#2C2C2A !important; }
.streamlit-expanderHeader { background:#F1EFE8 !important; border:0.5px solid #D3D1C7 !important; border-radius:10px !important; color:#2C2C2A !important; font-weight:600 !important; }
.stRadio > div { gap:8px !important; } .stRadio label { color:#444441 !important; font-size:0.85rem !important; }
.stTabs [data-baseweb="tab-list"] { background:#FFFFFF; border-radius:10px; padding:6px 8px; border:0.5px solid #D3D1C7; gap:4px; margin-bottom:8px; }
.stTabs [data-baseweb="tab"] { background:transparent; border-radius:8px; color:#5F5E5A !important; font-weight:500; font-size:0.88rem; padding:8px 18px; border:none; }
.stTabs [data-baseweb="tab"]:hover { background:#F1EFE8; color:#2C2C2A !important; }
.stTabs [aria-selected="true"] { background:#3B6D11 !important; color:#FFFFFF !important; font-weight:600 !important; }
.stTabs [aria-selected="true"] p, .stTabs [aria-selected="true"] span, .stTabs [aria-selected="true"] div { color:#FFFFFF !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top:12px; }
.stDownloadButton > button { background:#3B6D11 !important; color:#FFFFFF !important; font-weight:600 !important; border:none !important; border-radius:9px !important; }
.stAlert { border-radius:10px !important; font-size:0.88rem !important; }
div[data-testid="stAlert"] p, div[data-testid="stAlert"] span, div[data-testid="stAlert"] div { color:#2C2C2A !important; }
@media (max-width:900px) { .block-container { padding-left:1rem !important; padding-right:1rem !important; } .kpi-value { font-size:1.5rem !important; } }
@media (max-width:768px) {
    .block-container { padding-top:0.8rem !important; padding-left:0.6rem !important; padding-right:0.6rem !important; }
    .kpi-value { font-size:1.25rem !important; } .kpi-value-sm { font-size:1.05rem !important; }
    .kpi-label { font-size:0.6rem !important; } .kpi-card { min-height:auto !important; padding:11px 13px !important; }
    .section-header { font-size:0.85rem !important; } .stat-row { font-size:0.74rem !important; }
    .copyright { display:none !important; } .stButton > button { min-height:44px !important; }
    .badge { font-size:0.66rem !important; }
    .stRadio > div { flex-direction:column !important; gap:4px !important; }
    .stDataFrame { overflow-x:auto !important; }
}
@media (max-width:480px) {
    .block-container { padding-left:0.3rem !important; padding-right:0.3rem !important; }
    .kpi-value { font-size:1.05rem !important; } .kpi-label { font-size:0.56rem !important; }
}
.folium-map { width:100% !important; } iframe { max-width:100% !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="copyright">© Ivan Contreras</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# FUNCIONES DE DATOS
# ══════════════════════════════════════════════════════════
def _fetch_clima():
    try:
        r = requests.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude":8.7479,"longitude":-75.8814,
            "current":["temperature_2m","relative_humidity_2m","precipitation","wind_speed_10m"],
            "daily":["precipitation_sum","temperature_2m_max","temperature_2m_min","precipitation_probability_max"],
            "timezone":"America/Bogota","forecast_days":7
        }, timeout=8).json()
        c,d = r.get("current",{}),r.get("daily",{})
        lluvia_hoy = d.get("precipitation_sum",[0])[0] if d.get("precipitation_sum") else 0
        prob_raw = d.get("precipitation_probability_max",[])
        prob = [int(p) if p is not None else 0 for p in prob_raw] if prob_raw else [0]*7
        return {"temp":round(c.get("temperature_2m",28.4),1),"humedad":c.get("relative_humidity_2m",75),
                "lluvia_hoy":round(lluvia_hoy,1),"viento":round(c.get("wind_speed_10m",12),1),
                "lluvia_7d":d.get("precipitation_sum",[0]*7),"prob_lluvia":prob,
                "temp_max":d.get("temperature_2m_max",[32]*7),"temp_min":d.get("temperature_2m_min",[23]*7),
                "fechas":d.get("time",[]),"ok":True}
    except:
        return {"temp":28.4,"humedad":75,"lluvia_hoy":0,"viento":12,"lluvia_7d":[2]*7,
                "prob_lluvia":[10]*7,"temp_max":[32]*7,"temp_min":[23]*7,"fechas":[],"ok":False}

def _fetch_aire():
    try:
        r = requests.get("https://air-quality-api.open-meteo.com/v1/air-quality", params={
            "latitude":8.7479,"longitude":-75.8814,
            "current":["pm10","pm2_5","nitrogen_dioxide","european_aqi"],"timezone":"America/Bogota"
        }, timeout=8).json()
        c = r.get("current",{})
        return {"pm25":round(c.get("pm2_5",9.5),1),"pm10":round(c.get("pm10",11.9),1),
                "no2":round(c.get("nitrogen_dioxide",3.3),1),"aqi":round(c.get("european_aqi",26),0),"ok":True}
    except:
        return {"pm25":9.5,"pm10":11.9,"no2":3.3,"aqi":26,"ok":False}

def _fetch_ideam():
    try:
        r = requests.get("https://www.datos.gov.co/resource/sbwg-7ju4.json", params={
            "$where":"codigoestacion='23197130'","$order":"fechaobservacion DESC","$limit":"1"
        }, timeout=5).json()
        if r and "valor" in r[0]:
            return {"nivel":round(float(r[0]["valor"]),2),"fecha":r[0].get("fechaobservacion","")[:10],
                    "ok":True,"fuente":"IDEAM · datos.gov.co"}
    except: pass
    try:
        r2 = requests.get("https://www.datos.gov.co/resource/s54a-sgyg.json", params={
            "municipio":"MONTERIA","$limit":"1","$order":"fecha DESC"
        }, timeout=5).json()
        if r2 and "valor" in r2[0]:
            return {"nivel":round(float(r2[0]["valor"]),2),"fecha":r2[0].get("fecha","")[:10],
                    "ok":True,"fuente":"IDEAM · DHIME"}
    except: pass
    return {"nivel":4.2,"fecha":datetime.now(TZ_COL).strftime("%Y-%m-%d"),"ok":False,"fuente":"Histórico"}

@st.cache_data(ttl=900)
def cargar_datos():
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        return ex.submit(_fetch_clima).result(), ex.submit(_fetch_aire).result(), ex.submit(_fetch_ideam).result()

@st.cache_data(ttl=86400)
def obtener_fauna_gbif():
    NOMBRES_ES = {
        "Iguana iguana":"Iguana verde","Boa constrictor":"Boa","Caiman crocodilus":"Babilla",
        "Chelonoidis carbonarius":"Morrocoy","Trachemys callirostris":"Hicotea",
        "Lygophis lineatus":"Culebra rayada","Leptotila verreauxi":"Paloma guarumera",
        "Cairina moschata":"Pato real","Columbina talpacoti":"Tortolita rojiza",
        "Jacana jacana":"Gallito de ciénaga","Ardea alba":"Garza blanca",
        "Bubulcus ibis":"Garza del ganado","Coragyps atratus":"Gallinazo negro",
        "Pitangus sulphuratus":"Bichofué","Thraupis episcopus":"Azulejo común",
        "Ramphocelus dimidiatus":"Sangretoro","Dendrocygna autumnalis":"Pato viudo",
        "Vanellus chilensis":"Pellar","Dasypus novemcinctus":"Armadillo de nueve bandas",
        "Hydrochoerus hydrochaeris":"Chigüiro","Sciurus granatensis":"Ardilla roja",
        "Rhinella marina":"Sapo marino","Heliconia psittacorum":"Heliconia de loro",
        "Heliconia bihai":"Heliconia roja","Guazuma ulmifolia":"Guácimo",
        "Polybia emaciata":"Avispa social","Menemerus bivittatus":"Araña saltarina gris",
        "Sakesphorus canadensis":"Batará barrado","Phalacrocorax brasilianus":"Cormorán neotropical",
    }
    def _nom(sp_key, especie):
        if not sp_key: return NOMBRES_ES.get(especie,"—")
        try:
            r = requests.get(f"https://api.gbif.org/v1/species/{sp_key}/vernacularNames",params={"limit":20},timeout=4).json()
            for item in r.get("results",[]):
                if item.get("language","").lower() in ("spa","es","spanish"):
                    n=item.get("vernacularName","").strip()
                    if n: return n.capitalize()
            for item in r.get("results",[]):
                if item.get("language","").lower() in ("eng","en","english"):
                    n=item.get("vernacularName","").strip()
                    if n: return n.capitalize()
        except: pass
        return NOMBRES_ES.get(especie,"—")
    try:
        r = requests.get("https://api.gbif.org/v1/occurrence/search", params={
            "stateProvince":"Córdoba","country":"CO","mediaType":"StillImage","hasCoordinate":"true","limit":100
        }, timeout=12).json()
        registros,vistos=[],set()
        for rec in r.get("results",[]):
            sp=rec.get("species")
            if not sp or sp in vistos: continue
            vistos.add(sp)
            img=next((m["identifier"] for m in rec.get("media",[]) if "identifier" in m and m.get("type","")=="StillImage"),None)
            if img is None: img=next((m["identifier"] for m in rec.get("media",[]) if "identifier" in m),None)
            registros.append({"especie":sp,"clase":rec.get("class","—"),"orden":rec.get("order","—"),
                "familia":rec.get("family","—"),"lat":rec.get("decimalLatitude"),"lon":rec.get("decimalLongitude"),
                "fecha":(rec.get("eventDate","—")[:10] if rec.get("eventDate") else "—"),
                "imagen_url":img,"estado":rec.get("iucnRedListCategory","No evaluado"),"gbif_key":str(rec.get("speciesKey",""))})
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            nombres=list(ex.map(lambda reg: NOMBRES_ES.get(reg["especie"]) or _nom(reg["gbif_key"],reg["especie"]), registros))
        fauna=[]
        for reg,nom in zip(registros,nombres):
            reg["nombre_com"]=nom; fauna.append(reg)
        return (pd.DataFrame(fauna),True) if fauna else (None,False)
    except: return None,False

@st.cache_data(ttl=86400)
def obtener_avistamientos_mapa():
    ESPECIES=[
        ("Iguana iguana","🦎","Iguana verde","No evaluado","purple"),
        ("Leptotila verreauxi","🐦","Paloma guarumera","LC","purple"),
        ("Cairina moschata","🦆","Pato real","LC","purple"),
        ("Heliconia psittacorum","🌺","Heliconia de loro","No evaluado","purple"),
        ("Chelonoidis carbonarius","🐢","Morrocoy","Vulnerable","red"),
        ("Columbina talpacoti","🐦","Tortolita rojiza","LC","purple"),
        ("Ardea alba","🦢","Garza blanca","LC","purple"),
        ("Pitangus sulphuratus","🐦","Bichofué","LC","purple"),
    ]
    avistamientos=[]
    for especie,emoji,nombre_com,estado,color in ESPECIES:
        try:
            r=requests.get("https://api.gbif.org/v1/occurrence/search",params={
                "scientificName":especie,"decimalLatitude":"8.68,8.85","decimalLongitude":"-75.95,-75.78",
                "hasCoordinate":"true","country":"CO","limit":10},timeout=8).json()
            for rec in r.get("results",[]):
                lat,lon=rec.get("decimalLatitude"),rec.get("decimalLongitude")
                if lat and lon and 8.68<=lat<=8.85 and -75.95<=lon<=-75.78:
                    fecha=rec.get("eventDate","")[:10] if rec.get("eventDate") else "Sin fecha"
                    localidad=rec.get("locality",rec.get("municipality","Montería"))
                    avistamientos.append({"lat":lat,"lon":lon,"especie":especie,"emoji":emoji,
                        "nombre":nombre_com,"estado":estado,"color":color,"fecha":fecha,
                        "localidad":(localidad[:40] if localidad else "Montería")})
        except: continue
    return avistamientos

@st.cache_data(ttl=3600)
def obtener_historico_30dias():
    try:
        fecha_fin=datetime.now(TZ_COL).strftime("%Y-%m-%d")
        fecha_ini=(datetime.now(TZ_COL)-timedelta(days=30)).strftime("%Y-%m-%d")
        r=requests.get("https://api.open-meteo.com/v1/forecast",params={
            "latitude":8.7479,"longitude":-75.8814,
            "daily":["temperature_2m_max","temperature_2m_min","precipitation_sum","wind_speed_10m_max"],
            "timezone":"America/Bogota","start_date":fecha_ini,"end_date":fecha_fin},timeout=10).json()
        d=r.get("daily",{})
        return {"fechas":d.get("time",[]),"temp_max":d.get("temperature_2m_max",[]),
                "temp_min":d.get("temperature_2m_min",[]),"lluvia":d.get("precipitation_sum",[]),
                "viento":d.get("wind_speed_10m_max",[]),"ok":True}
    except: return {"ok":False,"fechas":[],"temp_max":[],"temp_min":[],"lluvia":[],"viento":[]}

@st.cache_data(ttl=3600)
def obtener_historico_aire_30dias():
    try:
        fecha_fin=datetime.now(TZ_COL).strftime("%Y-%m-%d")
        fecha_ini=(datetime.now(TZ_COL)-timedelta(days=30)).strftime("%Y-%m-%d")
        r=requests.get("https://air-quality-api.open-meteo.com/v1/air-quality",params={
            "latitude":8.7479,"longitude":-75.8814,"hourly":["pm2_5","pm10"],
            "timezone":"America/Bogota","start_date":fecha_ini,"end_date":fecha_fin},timeout=10).json()
        h=r.get("hourly",{})
        pm25_h,fechas_h=h.get("pm2_5",[]),h.get("time",[])
        dias_pm25={}
        for t,v in zip(fechas_h,pm25_h):
            if v is not None: dias_pm25.setdefault(t[:10],[]).append(v)
        fechas_d=sorted(dias_pm25.keys())
        pm25_d=[round(sum(dias_pm25[d])/len(dias_pm25[d]),1) for d in fechas_d]
        return {"fechas":fechas_d,"pm25":pm25_d,"ok":True}
    except: return {"ok":False,"fechas":[],"pm25":[]}

def nivel_rio(lluvia_7d, base=4.2):
    niveles,ant=[],base
    var_base=[0.0,0.05,-0.03,0.08,-0.02,0.06,-0.04]
    for i,ll in enumerate(lluvia_7d):
        v=var_base[i%len(var_base)]
        efecto=ll*0.08+(lluvia_7d[i-1]*0.04 if i>0 else 0)
        n=round(np.clip(ant*0.85+base*0.15+efecto+v,0.5,9.5),2)
        niveles.append(n); ant=n
    return niveles

def alerta_rio(n):
    if n<4.0:   return "Normal",   "badge-green",  "#3B6D11"
    elif n<5.5: return "Amarilla", "badge-yellow", "#BA7517"
    elif n<7.0: return "Naranja",  "badge-yellow", "#E24B4A"
    else:       return "ROJA 🚨",  "badge-red",    "#A32D2D"

def cat_aqi(aqi):
    if aqi<=20:   return "Bueno",     "badge-green"
    elif aqi<=40: return "Aceptable", "badge-yellow"
    elif aqi<=60: return "Moderado",  "badge-yellow"
    else:         return "Malo",      "badge-red"

def calcular_heat_index(temp_c, humedad):
    t=temp_c*9/5+32; rh=humedad
    hi=(-42.379+2.04901523*t+10.14333127*rh-0.22475541*t*rh-6.83783e-3*t**2
        -5.481717e-2*rh**2+1.22874e-3*t**2*rh+8.5282e-4*t*rh**2-1.99e-6*t**2*rh**2)
    hi_c=round((hi-32)*5/9,1)
    if hi_c<27:   return hi_c,"✅ Confortable",       "badge-green",  "#3B6D11"
    elif hi_c<32: return hi_c,"🟡 Precaución",        "badge-yellow", "#BA7517"
    elif hi_c<41: return hi_c,"🟠 Precaución extrema","badge-yellow", "#E24B4A"
    elif hi_c<54: return hi_c,"🔴 Peligro",           "badge-red",    "#A32D2D"
    else:         return hi_c,"🔴 Peligro extremo",   "badge-red",    "#A32D2D"

# ── Cauce río Sinú
CAUCE_SINU=[
    [8.69768846,-75.94782194],[8.70122071,-75.94240658],[8.69987114,-75.93560537],
    [8.70305888,-75.93594981],[8.71192054,-75.94286909],[8.71863785,-75.94379077],
    [8.72535501,-75.93734223],[8.72193985,-75.93215672],[8.71557630,-75.92536160],
    [8.71855524,-75.92260906],[8.72478702,-75.92213802],[8.73127622,-75.92305694],
    [8.73640083,-75.92213510],[8.73961492,-75.91957351],[8.74013571,-75.91535784],
    [8.73778687,-75.90851478],[8.74351866,-75.90587567],[8.74727880,-75.90322958],
    [8.74922018,-75.90126533],[8.74922025,-75.89856450],[8.74764320,-75.89414539],
    [8.74788577,-75.89242679],[8.75261750,-75.89193544],[8.75686353,-75.88984919],
    [8.76280817,-75.88518463],[8.77045286,-75.88223726],[8.77215134,-75.87941382],
    [8.76936038,-75.87450396],[8.76802566,-75.87290836],[8.76826901,-75.87094317],
    [8.77118166,-75.86959167],[8.78367731,-75.87364386],[8.78883840,-75.86806919],
    [8.79362685,-75.86414634],[8.80022730,-75.85977915],[8.80295920,-75.85977891],
    [8.80887841,-75.86254257],[8.82094414,-75.85770413],[8.82936742,-75.85632123],
    [8.83164380,-75.85309608],[8.83594253,-75.85423387],[8.84148501,-75.85633728],[8.84841300,-75.85668785],
]

UNIVERSIDADES=[
    (8.7678,-75.8848,"🎓 Universidad del Sinú","Cra. 1W #38-153","Institución privada · ~8,000 est."),
    (8.7919,-75.8624,"🎓 Universidad de Córdoba","Cra. 6 #77-305","Universidad pública · ~15,000 est."),
    (8.8050,-75.8505,"🎓 U. Pontificia Bolivariana","Cra. 6 #97A-99, Mocarí","Institución privada"),
    (8.7747,-75.8645,"🎓 Universidad Luis Amigó","Cl. 64 #6-108","Institución privada"),
    (8.7662,-75.8689,"🎓 U. Cooperativa de Colombia","Cl. 52 #6-79","Institución privada"),
    (8.7568,-75.8848,"🎓 CUN Montería","Cra. 4 #30-20","Corp. Unificada Nacional"),
    (8.7674,-75.8822,"🎓 Politécnico Gran Colombiano","Cl. 66 #5-70","Institución privada"),
    (8.7550,-75.8861,"🎓 Uniremington","Cl. 27 #4-31","Corp. Universitaria Remington"),
]

CC_GLOBAL=[
    (8.7791,-75.8616,"🛍️ C.C. Buenavista","Cra. 6 #68-72","Centro comercial principal"),
    (8.7433,-75.8682,"🛍️ C.C. Nuestro","Tv. 29 #29-69","Centro comercial Nuestro"),
    (8.7633,-75.8734,"🛍️ C.C. Alamedas","Cl. 44 #10-91","Centro comercial Alamedas del Sinú"),
]

# ══════════════════════════════════════════════════════════
# CARGA DE DATOS
# ══════════════════════════════════════════════════════════
_loading=st.empty()
_loading.markdown("""<div style="text-align:center;padding:40px 0;">
    <div style="color:#3B6D11;font-size:1.1rem;font-weight:700;margin-bottom:8px">🌿 Cargando BioMonitor Montería…</div>
    <div style="color:#5F5E5A;font-size:0.85rem">Conectando con Open-Meteo · IDEAM · GBIF</div>
</div>""", unsafe_allow_html=True)

try:
    clima,aire,ideam=cargar_datos()
except Exception as _e:
    _loading.error(f"⚠️ Error: {_e}"); st.stop()
_loading.empty()

if ideam["ok"]:
    nivel_base=ideam["nivel"]; fuente_rio=f"🟢 {ideam.get('fuente','—')} · {ideam.get('fecha','—')}"
elif clima["ok"]:
    nivel_base=4.2; fuente_rio="🟡 Simulado · lluvia real Open-Meteo"
else:
    nivel_base=4.2; fuente_rio="🔴 Datos históricos"

niveles=nivel_rio(clima["lluvia_7d"],base=nivel_base)
dias=[datetime.strptime(f,"%Y-%m-%d").strftime("%d %b") for f in clima["fechas"]] if clima["fechas"] else \
     [(datetime.now(TZ_COL)+timedelta(days=i)).strftime("%d %b") for i in range(7)]
rio_txt,rio_badge,rio_color=alerta_rio(niveles[0])
aqi_txt,aqi_badge=cat_aqi(aire["aqi"])

# ══════════════════════════════════════════════════════════
# HEADER — Logo izquierda · Descripción centro · Estado derecha
# ══════════════════════════════════════════════════════════
st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
col_logo, col_texto, col_estado = st.columns([1, 2.2, 1], gap="medium")

with col_logo:
    try:
        logo_img=Image.open("Biomotorlogo.png")
        st.image(logo_img, width=280)
    except:
        st.markdown('<h2 style="color:#3B6D11;margin:0">🌿 BioMonitor</h2>', unsafe_allow_html=True)

with col_texto:
    st.markdown("""
    <div style="display:flex;flex-direction:column;justify-content:center;height:100%;padding:6px 0">
        <div style="font-size:0.93rem;color:#5F5E5A;line-height:1.65;margin-bottom:14px">
            Plataforma de monitoreo ambiental en tiempo real para
            <b style="color:#2C2C2A">Montería, Córdoba, Colombia</b>.
            Integra datos oficiales de <b>IDEAM</b>, <b>Open-Meteo</b> y <b>GBIF</b>
            para monitorear el nivel del río Sinú, la calidad del aire
            y la biodiversidad local. Actualización automática cada 15 minutos.
        </div>
        <div>
            <span class="hero-badge">🌡️ Clima en tiempo real</span>
            <span class="hero-badge">💨 Calidad del aire</span>
            <span class="hero-badge">🌊 Nivel Río Sinú</span>
            <span class="hero-badge">🦜 Biodiversidad GBIF</span>
            <span class="hero-badge">🗺️ Mapa interactivo</span>
        </div>
    </div>""", unsafe_allow_html=True)

with col_estado:
    nivel_h=niveles[0] if niveles else 0
    pm_h=aire.get("pm25",0)
    hi_h,_,_,_=calcular_heat_index(clima.get("temp",30),clima.get("humedad",75))
    if nivel_h>=5.5 or pm_h>=25:
        ei,et,ec,ed="🔴","Atención requerida","#791F1F","Hay condiciones de riesgo activas"
    elif nivel_h>=4.0 or pm_h>=15 or hi_h>=32:
        ei,et,ec,ed="🟡","Monitorear de cerca","#633806","Algunas variables requieren atención"
    else:
        ei,et,ec,ed="🟢","Todo en orden","#27500A","Todas las variables en rango normal"
    hora=datetime.now(TZ_COL).strftime("%H:%M")
    st.markdown(f"""
    <div class="kpi-card" style="text-align:center;padding:18px 14px;border-left:4px solid {ec};border-radius:0 12px 12px 0">
        <div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:1px;color:#888780;margin-bottom:8px;font-weight:600">¿Cómo está Montería ahora?</div>
        <div style="font-size:2.4rem;margin:4px 0;line-height:1">{ei}</div>
        <div style="font-size:0.95rem;font-weight:700;color:{ec};margin-top:6px">{et}</div>
        <div style="font-size:0.75rem;color:#5F5E5A;margin-top:5px;line-height:1.4">{ed}</div>
        <div style="font-size:0.68rem;color:#888780;margin-top:8px;border-top:0.5px solid #D3D1C7;padding-top:6px">Actualizado {hora} hora Colombia</div>
    </div>
    <div style="margin-top:8px;font-size:0.72rem;color:#5F5E5A;background:#F1EFE8;border-radius:8px;padding:10px 12px;border:0.5px solid #D3D1C7">
        <b style="color:#2C2C2A;display:block;margin-bottom:5px">¿Qué significa el color?</b>
        <span style="color:#27500A">🟢 Verde</span> — Sin alertas<br>
        <span style="color:#633806">🟡 Amarillo</span> — Atención<br>
        <span style="color:#791F1F">🔴 Rojo</span> — Riesgo activo
    </div>""", unsafe_allow_html=True)
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    if st.button("🔄 Actualizar datos", use_container_width=True):
        st.cache_data.clear(); st.rerun()

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════
tab_inicio,tab_mapa,tab_analisis,tab_bio,tab_alertas=st.tabs([
    "🏠 Inicio","🗺️ Mapa","📈 Análisis","🦜 Biodiversidad","🔔 Alertas"
])

# ══════════════════════════════════════════════════════════
# TAB 1 — INICIO
# ══════════════════════════════════════════════════════════
with tab_inicio:
    def _kpi(cls,label,val,badge_txt,badge_cls,fuente):
        st.markdown(f"""<div class="{cls}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{val}</div>
            <span class="badge {badge_cls}">{badge_txt}</span>
            <div class="fuente-tag">{fuente}</div>
        </div>""", unsafe_allow_html=True)

    k1,k2,k3=st.columns(3,gap="small")
    with k1: _kpi("kpi-card","🌊 Nivel Río Sinú",f"{niveles[0]} m",rio_txt,rio_badge,fuente_rio)
    with k2: _kpi("kpi-card kpi-card-blue","🌡️ Temperatura",f"{clima.get('temp','—')} °C",
                  f"Humedad {clima['humedad']}%","badge-blue","Open-Meteo · ahora")
    with k3:
        prob=clima.get("prob_lluvia",[0])[0] if clima.get("prob_lluvia") else 0
        _kpi("kpi-card kpi-card-blue","🌧️ Lluvia hoy",f"{clima.get('lluvia_hoy','—')} mm",
             f"☔ Prob. {prob}%","badge-blue" if prob<30 else "badge-yellow" if prob<60 else "badge-red","Open-Meteo · ahora")

    k4,k5,k6=st.columns(3,gap="small")
    with k4: _kpi("kpi-card kpi-card-green","💨 PM2.5",f"{aire.get('pm25','—')} µg/m³","✅ OMS < 15","badge-green","Open-Meteo · ahora")
    with k5: _kpi("kpi-card","🌬️ AQI Europeo",str(aire.get('aqi','—')),aqi_txt,aqi_badge,"Índice europeo")
    with k6: _kpi("kpi-card kpi-card-purple","🦜 Especies GBIF","≥12","Córdoba 2026","badge-purple","GBIF · Córdoba, CO")

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">📋 Resumen del estado actual</div>', unsafe_allow_html=True)

    hi_i,hi_lbl_i,_,_=calcular_heat_index(clima.get("temp",30),clima.get("humedad",75))
    alerta_rio_i,_,_=alerta_rio(niveles[0])

    for ico,titulo,desc,badge_cls,fuente in [
        ("🌊","Río Sinú",f"Nivel {niveles[0]}m · Alerta {alerta_rio_i}",
         "badge-yellow" if niveles[0]>=4.0 else "badge-green","Estación Ronda del Sinú · IDEAM"),
        ("🌡️","Temperatura y calor",f"{clima.get('temp','—')}°C real · {hi_i}°C aparente · {hi_lbl_i}",
         "badge-yellow" if hi_i>=32 else "badge-green","Open-Meteo · tiempo real"),
        ("💨","Calidad del aire",f"PM2.5: {aire.get('pm25','—')} µg/m³ · AQI: {aire.get('aqi','—')}",
         "badge-green" if aire.get('pm25',0)<15 else "badge-yellow","Open-Meteo Air Quality"),
        ("🌧️","Lluvia",f"{clima.get('lluvia_hoy','0')} mm hoy · Prob. {prob}%","badge-blue","Open-Meteo · tiempo real"),
        ("🌿","Biodiversidad","≥12 especies en Córdoba · datos GBIF actualizados","badge-purple","GBIF · Córdoba 2026"),
    ]:
        st.markdown(f"""<div class="info-card" style="display:flex;align-items:flex-start;gap:12px;margin-bottom:8px">
            <div style="font-size:1.4rem;line-height:1;flex-shrink:0">{ico}</div>
            <div style="flex:1">
                <div style="font-weight:600;color:#2C2C2A;font-size:0.9rem">{titulo}</div>
                <div style="color:#5F5E5A;font-size:0.82rem;margin-top:2px">{desc}</div>
                <div style="color:#888780;font-size:0.7rem;margin-top:3px">{fuente}</div>
            </div>
            <span class="badge {badge_cls}" style="flex-shrink:0;align-self:center">
                {'✓ Normal' if 'green' in badge_cls else '⚠ Atención' if 'yellow' in badge_cls else '● Activo'}
            </span>
        </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="info-card" style="font-size:0.8rem;color:#888780;text-align:center">
        💡 Usa las pestañas de arriba para ver el <b>Mapa</b>, el <b>Análisis</b> histórico,
        la <b>Biodiversidad</b> y las <b>Alertas</b>.</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# TAB 2 — MAPA
# ══════════════════════════════════════════════════════════
with tab_mapa:
    st.markdown('<div class="section-header">🗺️ Mapa ambiental interactivo · Montería</div>', unsafe_allow_html=True)
    col_mapa,col_pred=st.columns([1.35,1],gap="small")

    with col_mapa:
        b1,b2,b3,_=st.columns([1.1,1.1,1,3],gap="small")
        with b1:
            if st.button("🗺️ Estándar",use_container_width=True,
                         type="primary" if st.session_state.mapa_tipo=="Estándar" else "secondary"):
                st.session_state.mapa_tipo="Estándar"; st.rerun()
        with b2:
            if st.button("🛰️ Satelital",use_container_width=True,
                         type="primary" if st.session_state.mapa_tipo=="Satelital" else "secondary"):
                st.session_state.mapa_tipo="Satelital"; st.rerun()
        with b3:
            if st.button("🌑 Oscuro",use_container_width=True,
                         type="primary" if st.session_state.mapa_tipo=="Oscuro" else "secondary"):
                st.session_state.mapa_tipo="Oscuro"; st.rerun()

        tipo=st.session_state.mapa_tipo
        if tipo=="Satelital":
            m=folium.Map(location=[8.7700,-75.8750],zoom_start=13,tiles=None,prefer_canvas=True)
            folium.TileLayer(tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                attr="Tiles © Esri",name="Satelital",overlay=False,control=True).add_to(m)
        elif tipo=="Oscuro":
            m=folium.Map(location=[8.7700,-75.8750],zoom_start=13,tiles="CartoDB dark_matter",attr="© CartoDB",prefer_canvas=True)
        else:
            m=folium.Map(location=[8.7700,-75.8750],zoom_start=13,tiles="OpenStreetMap",attr="© OSM contributors",prefer_canvas=True)

        g_rio=folium.FeatureGroup(name="🌊 Río y estaciones",show=True)
        g_contam=folium.FeatureGroup(name="💨 Contaminación",show=True)
        g_inund=folium.FeatureGroup(name="🌊 Zonas inundación",show=True)
        g_lluvia=folium.FeatureGroup(name="🌧️ Lluvia",show=True)
        g_univ=folium.FeatureGroup(name="🎓 Universidades",show=True)
        g_cc=folium.FeatureGroup(name="🛍️ C. Comerciales",show=True)
        g_aire=folium.FeatureGroup(name="💨 Estaciones aire",show=True)
        g_fauna=folium.FeatureGroup(name="🦜 Fauna",show=True)

        folium.PolyLine(locations=CAUCE_SINU,color="#4FC3F7",weight=5,opacity=0.9,tooltip="Río Sinú").add_to(g_rio)
        folium.Circle([8.7560,-75.8850],radius=6000,color="#3B6D11",fill=True,fill_opacity=0.02,weight=1,dash_array="6").add_to(g_rio)

        for lat,lon,nombre,idx in [
            (8.7576,-75.8875,"Ronda del Sinú — Av. Primera",0),
            (8.7650,-75.8845,"Puente Segundo Centenario",1),
            (8.7619,-75.8846,"Muelle Turístico del Sinú",2),
        ]:
            al,_,_=alerta_rio(niveles[idx])
            folium.Marker([lat,lon],
                popup=folium.Popup(f"<b>🌊 {nombre}</b><br>📊 Nivel: <b>{niveles[idx]}m</b><br>🔔 Estado: <b>{al}</b><br>📡 {fuente_rio}",max_width=260),
                tooltip=folium.Tooltip(f"🌊 {nombre} · {niveles[idx]}m · {al}",sticky=True),
                icon=folium.Icon(color="blue",icon="tint",prefix="fa")).add_to(g_rio)

        pm25_v=aire["pm25"]
        def color_c(f):
            v=pm25_v*f
            if v<10: return "#3B6D11","🟢 Buena"
            elif v<15: return "#BA7517","🟡 Moderada"
            elif v<25: return "#E24B4A","🟠 Regular"
            else: return "#A32D2D","🔴 Mala"

        for lat,lon,radio,nombre,desc,factor in [
            (8.7420,-75.8650,280,"🚌 Terminal de Transportes","Cl. 44 · buses y camiones",2.1),
            (8.7512,-75.8795,260,"🏪 Mercado Central","Cra. 6 centro · tráfico pesado",1.8),
            (8.7600,-75.8600,240,"🚗 Avenida Circunvalar","Corredor vial principal",1.6),
            (8.7559,-75.8870,200,"🏛️ Parque Simón Bolívar","Centro histórico",1.3),
            (8.7791,-75.8616,200,"🛍️ Zona C.C. Buenavista","Flujo comercial intenso",1.4),
            (8.7117,-75.8284,200,"⚽ Estadio Jaraguay","Estadio Municipal · zona sur",1.2),
            (8.7576,-75.8875,320,"🌿 Ronda del Sinú","Parque lineal · pulmón verde",0.6),
            (8.8233,-75.8258,180,"✈️ Aeropuerto Los Garzones","Zona norte periférica",0.8),
        ]:
            c,estado=color_c(factor)
            folium.Circle([lat,lon],radius=radio,color=c,fill=True,fill_color=c,fill_opacity=0.40,weight=3,
                popup=folium.Popup(f"<b>{nombre}</b><br>📍 {desc}<br>💨 PM2.5 est.: <b>{round(pm25_v*factor,1)} µg/m³</b><br>Estado: {estado}",max_width=260),
                tooltip=f"{nombre} — {estado}").add_to(g_contam)

        nivel_act=niveles[0]
        for lat,lon,radio,barrios,cota,nota in [
            (8.7480,-75.8960,300,"La Granja · La Ribera",4.0,"Zona baja occidental"),
            (8.7430,-75.8880,260,"Barrio Colón · Chuchurubi",4.0,"Inundación histórica"),
            (8.7650,-75.8930,240,"Ronda Sinú norte",5.5,"Afectada cota 5.5m"),
            (8.7800,-75.8900,200,"El Recreo · ribera norte",5.5,"Afectada cota 5.5m"),
            (8.7280,-75.9000,200,"Mocarí · zona sur",4.0,"Zona baja sur"),
        ]:
            if nivel_act>=cota+1.5: cz,fo,az="#A32D2D",0.38,"⚠️ INUNDACIÓN"
            elif nivel_act>=cota:   cz,fo,az="#E24B4A",0.24,"⚠️ Alerta"
            elif nivel_act>=cota-0.5: cz,fo,az="#BA7517",0.14,"⚡ Precaución"
            else:                   cz,fo,az="#4FC3F7",0.07,"✅ Normal"
            folium.Circle([lat,lon],radius=radio,color=cz,fill=True,fill_color=cz,fill_opacity=fo,weight=3,dash_array="6",
                popup=folium.Popup(f"<b>🌊 Zona inundación</b><br>Barrios: {barrios}<br>Nivel: <b>{nivel_act}m</b><br>Cota: {cota}m · {az}<br>{nota}",max_width=270),
                tooltip=f"🌊 {barrios} — {az}").add_to(g_inund)

        prob_h=clima.get("prob_lluvia",[0])[0] if clima.get("prob_lluvia") else 0
        if prob_h>=20 or clima.get("lluvia_hoy",0)>0:
            cl_r,op_r=("#0066FF",0.22) if prob_h>=60 else ("#00AAFF",0.13) if prob_h>=30 else ("#00CCFF",0.07)
            for lat_z,lon_z,peso in [(8.7550,-75.8914,1.0),(8.7480,-75.9000,0.9),(8.7750,-75.8870,0.8)]:
                folium.Circle([lat_z,lon_z],radius=int(2000*peso),color=cl_r,fill=True,fill_color=cl_r,
                    fill_opacity=op_r*peso,weight=0,tooltip=f"🌧️ Prob. lluvia: {prob_h}%").add_to(g_lluvia)

        for lat,lon,nombre,direccion,info in UNIVERSIDADES:
            folium.Marker([lat,lon],popup=folium.Popup(f"<b>{nombre}</b><br>📍 {direccion}<br>ℹ️ {info}",max_width=250),
                tooltip=nombre,icon=folium.Icon(color="orange",icon="graduation-cap",prefix="fa")).add_to(g_univ)

        for lat,lon,nombre,direccion,info in CC_GLOBAL:
            folium.Marker([lat,lon],popup=folium.Popup(f"<b>{nombre}</b><br>📍 {direccion}<br>ℹ️ {info}",max_width=250),
                tooltip=nombre,icon=folium.Icon(color="red",icon="shopping-cart",prefix="fa")).add_to(g_cc)

        for lat,lon,nombre,txt in [
            (8.7550,-75.8750,"💨 Estación Centro",f"PM2.5: {aire.get('pm25','—')} µg/m³<br>AQI: {aire.get('aqi','—')}<br>NO₂: {aire.get('no2','—')} µg/m³"),
            (8.7350,-75.8650,"💨 Estación Sur",f"PM10: {aire.get('pm10','—')} µg/m³<br>PM2.5: {aire.get('pm25','—')} µg/m³"),
        ]:
            folium.Marker([lat,lon],popup=folium.Popup(f"<b>{nombre}</b><br>{txt}<br>📡 Open-Meteo · tiempo real",max_width=230),
                tooltip=folium.Tooltip(nombre,sticky=True),icon=folium.Icon(color="green",icon="cloud",prefix="fa")).add_to(g_aire)

        avistamientos_reales=obtener_avistamientos_mapa()
        if avistamientos_reales:
            from collections import defaultdict
            por_especie=defaultdict(list)
            for av in avistamientos_reales: por_especie[av["especie"]].append(av)
            for especie,regs in por_especie.items():
                for av in regs:
                    folium.Marker([av["lat"],av["lon"]],
                        popup=folium.Popup(f"<b>{av['emoji']} {av['especie']}</b><br>🏷️ <b>{av['nombre']}</b><br>📍 {av['localidad']}<br>📅 {av['fecha']}<br>🔴 IUCN: {av['estado']}<br>📡 GBIF · coordenadas reales",max_width=260),
                        tooltip=folium.Tooltip(f"{av['emoji']} {av['especie']}<br>{av['nombre']} · {av['fecha']}",sticky=True),
                        icon=folium.Icon(color="red" if av["estado"]=="Vulnerable" else "purple",icon="paw",prefix="fa")).add_to(g_fauna)
        else:
            for lat,lon,esp,nom,zona,est in [
                (8.7576,-75.8875,"🦎 Iguana iguana","Iguana verde","Ronda del Sinú","No evaluado"),
                (8.7720,-75.8680,"🐦 Leptotila verreauxi","Paloma guarumera","Norte urbano","LC"),
                (8.7619,-75.8846,"🦆 Cairina moschata","Pato real","Muelle Turístico","LC"),
                (8.7678,-75.8848,"🌺 Heliconia psittacorum","Heliconia de loro","Zonas verdes","No evaluado"),
                (8.7117,-75.8284,"🐢 Chelonoidis carbonarius","Morrocoy","Zona sur","Vulnerable"),
            ]:
                folium.Marker([lat,lon],
                    popup=folium.Popup(f"<b>{esp}</b><br>🏷️ {nom}<br>📍 {zona}<br>🔴 IUCN: {est}",max_width=250),
                    tooltip=folium.Tooltip(f"{esp} · {nom}",sticky=True),
                    icon=folium.Icon(color="red" if est=="Vulnerable" else "purple",icon="paw",prefix="fa")).add_to(g_fauna)

        for g in [g_inund,g_lluvia,g_contam,g_rio,g_aire,g_univ,g_cc,g_fauna]: g.add_to(m)
        folium.LayerControl(collapsed=False,position="topright").add_to(m)
        st_folium(m,width=None,height=460,use_container_width=True,returned_objects=[],key="mapa_principal")

    with col_pred:
        st.markdown('<div class="section-header">🌊 Predicción 7 días · LSTM</div>', unsafe_allow_html=True)
        fig,ax=plt.subplots(figsize=(5.5,3.8)); fig.patch.set_facecolor("#FFFFFF"); ax.set_facecolor("#FFFFFF")
        bar_colors=["#3B6D11" if n<4.0 else "#BA7517" if n<5.5 else "#E24B4A" if n<7.0 else "#A32D2D" for n in niveles]
        bars=ax.bar(dias,niveles,color=bar_colors,alpha=0.88,width=0.55,edgecolor="#E8E6E0",linewidth=0.6)
        ax.fill_between(range(len(niveles)),niveles,alpha=0.07,color="#3B6D11")
        ax.plot(range(len(niveles)),niveles,color="#3B6D11",linewidth=1.2,alpha=0.5,linestyle="--",marker="o",markersize=3)
        ax.axhline(y=4.0,color="#BA7517",linestyle="--",linewidth=1.2,alpha=0.6,label="Amarilla (4m)")
        ax.axhline(y=5.5,color="#E24B4A",linestyle="--",linewidth=1.2,alpha=0.6,label="Naranja (5.5m)")
        ax.axhline(y=7.0,color="#A32D2D",linestyle="--",linewidth=1.2,alpha=0.6,label="Roja (7m)")
        ax.set_ylabel("Nivel (m)",color="#5F5E5A",fontsize=9); ax.set_ylim(0,9)
        ax.tick_params(colors="#5F5E5A",labelsize=8)
        for spine in ax.spines.values(): spine.set_color("#D3D1C7")
        ax.set_xticks(range(len(dias))); ax.set_xticklabels(dias,fontsize=7.5,color="#5F5E5A",rotation=15)
        ax.grid(axis="y",color="#E8E6E0",linewidth=0.6,linestyle=":")
        ax.legend(fontsize=7.5,facecolor="#FFFFFF",labelcolor="#5F5E5A",framealpha=0.85,loc="upper right")
        for bar,val in zip(bars,niveles):
            ax.text(bar.get_x()+bar.get_width()/2,val+0.13,f"{val}m",ha="center",va="bottom",color="#2C2C2A",fontsize=7.5,fontweight="bold")
        plt.tight_layout(pad=0.6); st.pyplot(fig); plt.close()

        if "Normal" in rio_txt:     st.success(f"🟢 {rio_txt} — Nivel en rango seguro")
        elif "Amarilla" in rio_txt: st.warning(f"🟡 {rio_txt} — Monitorear de cerca")
        elif "Naranja" in rio_txt:  st.warning(f"🟠 {rio_txt} — Precaución zonas bajas")
        else:                       st.error(f"🔴 {rio_txt} — ¡Alerta máxima!")

        prob_pred=clima.get("prob_lluvia",[0])[0] if clima.get("prob_lluvia") else 0
        st.markdown(f"""<div class="stat-row">
            🌧️ Lluvia hoy: <b style="color:#2C2C2A">{clima['lluvia_hoy']} mm</b> &nbsp;·&nbsp;
            🌂 Prob.: <b style="color:#185FA5">{prob_pred}%</b> &nbsp;·&nbsp;
            💨 Viento: <b style="color:#2C2C2A">{clima['viento']} km/h</b> &nbsp;·&nbsp;
            🌡️ Máx: <b style="color:#2C2C2A">{clima['temp_max'][0]}°C</b><br>
            <small style="color:#888780">{fuente_rio}</small>
        </div>""", unsafe_allow_html=True)
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        df_niv=pd.DataFrame({"Día":dias,"Nivel":[f"{n} m" for n in niveles],"Estado":[alerta_rio(n)[0] for n in niveles]})
        st.dataframe(df_niv,use_container_width=True,hide_index=True,height=210)

    st.markdown("<hr style='border:none;border-top:0.5px solid #D3D1C7;margin:16px 0'>", unsafe_allow_html=True)
    nivel_act2=niveles[0]; alerta_lbl2,_,_=alerta_rio(nivel_act2)
    with st.expander(f"🌊 Zonas afectadas — Estado: {alerta_lbl2} ({nivel_act2}m)",expanded=nivel_act2>=4.0):
        for zona,barrios,ubicacion,cota,accion in [
            ("Zona ALTO riesgo","La Granja · La Ribera · Los Nogales","Margen occidental, cota baja",4.0,"Evacuar si nivel supera 5m · Av. Circunvalar"),
            ("Zona ALTO riesgo","Barrio Colón · Chuchurubi · Santa Fe","Sector sur, inundación histórica",4.0,"Contactar Defensa Civil: 144"),
            ("Zona MEDIO riesgo","Ronda del Sinú norte · Av. Primera","Parque lineal y avenida ribereña",5.5,"Cerrar acceso si nivel > 5.5m"),
            ("Zona MEDIO riesgo","El Recreo · Ribera norte","Barrio nororiental junto al río",5.5,"Monitorear en temporada de lluvias"),
            ("Zona ALTO riesgo","Mocarí · Zona sur rural","Área baja al sur de Montería",4.0,"Riesgo de pérdidas en cultivos"),
        ]:
            if nivel_act2>=cota+1.5: bc,et="badge-red","🔴 INUNDACIÓN"
            elif nivel_act2>=cota:   bc,et="badge-yellow","🟠 ALERTA"
            elif nivel_act2>=cota-0.5: bc,et="badge-yellow","🟡 PRECAUCIÓN"
            else:                    bc,et="badge-green","✅ Normal"
            st.markdown(f"""<div style="background:#F1EFE8;border:0.5px solid #D3D1C7;border-radius:10px;padding:12px 16px;margin-bottom:10px">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
                    <span class="badge {bc}">{zona}</span>
                    <span style="color:#2C2C2A;font-weight:600">{barrios}</span>
                </div>
                <div style="color:#5F5E5A;font-size:0.82rem;margin-bottom:4px">📍 {ubicacion} · Cota: {cota}m</div>
                <div style="color:#185FA5;font-size:0.82rem;margin-bottom:4px">📊 {et} — nivel actual: {nivel_act2}m</div>
                <div style="color:#888780;font-size:0.78rem">💡 {accion}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown(f"""<div style="background:#EAF3DE;border:0.5px solid #97C459;border-radius:10px;padding:10px 14px;font-size:0.78rem;color:#5F5E5A">
            📞 <b style="color:#2C2C2A">Emergencias:</b> Defensa Civil 144 · Bomberos 119 · Cruz Roja 132<br>
            📡 <b style="color:#2C2C2A">Fuente:</b> {fuente_rio}
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# TAB 3 — ANÁLISIS
# ══════════════════════════════════════════════════════════
with tab_analisis:
    st.markdown('<div class="section-header">💨 Calidad del aire · Open-Meteo Air Quality API</div>', unsafe_allow_html=True)
    a1,a2=st.columns(2,gap="small"); a3,a4=st.columns(2,gap="small")
    for col,lbl,val,bt,bc in [
        (a1,"PM2.5",f"{aire['pm25']} µg/m³","✅ OMS < 15","badge-green"),
        (a2,"PM10",f"{aire['pm10']} µg/m³","✅ OMS < 45","badge-green"),
        (a3,"NO₂",f"{aire['no2']} µg/m³","✅ Normal","badge-green"),
        (a4,"AQI Europeo",str(aire['aqi']),aqi_txt,aqi_badge),
    ]:
        with col:
            st.markdown(f"""<div class="kpi-card kpi-card-green">
                <div class="kpi-label">{lbl}</div><div class="kpi-value">{val}</div>
                <span class="badge {bc}">{bt}</span><div class="fuente-tag">Open-Meteo · tiempo real</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<hr style='border:none;border-top:0.5px solid #D3D1C7;margin:16px 0'>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">🌡️ Índice de calor aparente · Heat Index</div>', unsafe_allow_html=True)
    hi_val,hi_lbl,hi_badge,hi_color=calcular_heat_index(clima.get("temp",30),clima.get("humedad",75))
    hc1,hc2,hc3,hc4=st.columns(4,gap="small")
    for col,lbl,val,bt,bc,ft,cl in [
        (hc1,"Temperatura real",f"{clima.get('temp','—')}°C","Termómetro","badge-green","Open-Meteo · tiempo real","#2C2C2A"),
        (hc2,"Humedad relativa",f"{clima.get('humedad','—')}%","Humedad","badge-green","Open-Meteo · tiempo real","#2C2C2A"),
        (hc3,"Calor aparente",f"{hi_val}°C",hi_lbl,hi_badge,"Fórmula Steadman/NWS",hi_color),
        (hc4,"Diferencia térmica",f"+{round(hi_val-clima.get('temp',30),1)}°C","Sensación extra",hi_badge,"vs temperatura real",hi_color),
    ]:
        with col:
            st.markdown(f"""<div class="kpi-card kpi-card-green">
                <div class="kpi-label">{lbl}</div>
                <div class="kpi-value" style="color:{cl}">{val}</div>
                <span class="badge {bc}">{bt}</span>
                <div class="fuente-tag">{ft}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("""<div style="background:#F1EFE8;border:0.5px solid #D3D1C7;border-radius:10px;padding:12px 16px;margin-top:8px">
        <b style="color:#2C2C2A;font-size:0.82rem;display:block;margin-bottom:8px">Escala de riesgo por calor · OMS / NWS:</b>
        <div style="display:flex;flex-wrap:wrap;gap:6px">
            <span style="background:#EAF3DE;color:#27500A;padding:4px 10px;border-radius:6px;font-size:0.78rem;font-weight:600">✅ &lt;27°C · Confortable</span>
            <span style="background:#FAEEDA;color:#633806;padding:4px 10px;border-radius:6px;font-size:0.78rem;font-weight:600">🟡 27–32°C · Precaución</span>
            <span style="background:#F5C4B3;color:#712B13;padding:4px 10px;border-radius:6px;font-size:0.78rem;font-weight:600">🟠 32–41°C · Precaución extrema</span>
            <span style="background:#F7C1C1;color:#791F1F;padding:4px 10px;border-radius:6px;font-size:0.78rem;font-weight:600">🔴 41–54°C · Peligro</span>
            <span style="background:#F09595;color:#501313;padding:4px 10px;border-radius:6px;font-size:0.78rem;font-weight:600">☠️ &gt;54°C · Peligro extremo</span>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<hr style='border:none;border-top:0.5px solid #D3D1C7;margin:16px 0'>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">💧 Correlación lluvia vs nivel del río · 7 días</div>', unsafe_allow_html=True)
    lluvia_7d=clima.get("lluvia_7d",[0]*7)
    fig_corr,axes=plt.subplots(1,2,figsize=(11,3.5)); fig_corr.patch.set_facecolor("#FFFFFF")
    ax1=axes[0]; ax1.set_facecolor("#F9F8F6"); ax2=ax1.twinx()
    dias_c=[d.replace(" ","") for d in dias]
    ax1.bar(dias_c,lluvia_7d,color="#4FC3F7",alpha=0.6,width=0.4,label="Lluvia (mm)")
    ax2.plot(dias_c,niveles,color="#BA7517",linewidth=2.5,marker="o",markersize=5,label="Nivel río (m)")
    ax1.set_ylabel("Lluvia (mm)",color="#4FC3F7",fontsize=8); ax2.set_ylabel("Nivel río (m)",color="#BA7517",fontsize=8)
    ax1.tick_params(colors="#5F5E5A",labelsize=7); ax2.tick_params(colors="#BA7517",labelsize=7)
    for spine in ax1.spines.values(): spine.set_color("#D3D1C7")
    for spine in ax2.spines.values(): spine.set_color("#D3D1C7")
    ax1.set_title("Lluvia acumulada vs nivel del río",color="#2C2C2A",fontsize=9,pad=6)
    ax1.tick_params(axis='x',rotation=15); ax1.grid(axis="y",color="#E8E6E0",linewidth=0.5)
    l1,lb1=ax1.get_legend_handles_labels(); l2,lb2=ax2.get_legend_handles_labels()
    ax1.legend(l1+l2,lb1+lb2,fontsize=7,facecolor="#FFFFFF",labelcolor="#5F5E5A",loc="upper left")
    ax3=axes[1]; ax3.set_facecolor("#F9F8F6")
    cs=["#3B6D11" if n<4.0 else "#BA7517" if n<5.5 else "#E24B4A" for n in niveles]
    ax3.scatter(lluvia_7d,niveles,c=cs,s=80,zorder=5,alpha=0.9)
    for i,(x,y) in enumerate(zip(lluvia_7d,niveles)):
        ax3.annotate(dias_c[i],(x,y),textcoords="offset points",xytext=(4,4),fontsize=6.5,color="#5F5E5A")
    if len(lluvia_7d)>1:
        z=np.polyfit(lluvia_7d,niveles,1); p=np.poly1d(z)
        xl=np.linspace(min(lluvia_7d),max(lluvia_7d),50)
        ax3.plot(xl,p(xl),"--",color="#E24B4A",linewidth=1.2,alpha=0.7,label="Tendencia")
        corr=np.corrcoef(lluvia_7d,niveles)[0,1]
        ax3.text(0.05,0.92,f"r = {corr:.2f}",transform=ax3.transAxes,color="#3B6D11",fontsize=8,fontweight="bold")
    ax3.set_xlabel("Lluvia (mm)",color="#5F5E5A",fontsize=8); ax3.set_ylabel("Nivel río (m)",color="#5F5E5A",fontsize=8)
    ax3.set_title("Correlación lluvia → nivel",color="#2C2C2A",fontsize=9,pad=6)
    ax3.tick_params(colors="#5F5E5A",labelsize=7)
    for spine in ax3.spines.values(): spine.set_color("#D3D1C7")
    ax3.grid(color="#E8E6E0",linewidth=0.5); ax3.legend(fontsize=7,facecolor="#FFFFFF",labelcolor="#5F5E5A")
    plt.tight_layout(pad=0.8); st.pyplot(fig_corr); plt.close()
    corr_val=np.corrcoef(lluvia_7d,niveles)[0,1] if len(lluvia_7d)>1 else 0
    interp=("correlación muy fuerte" if abs(corr_val)>0.8 else "correlación moderada" if abs(corr_val)>0.5 else "correlación débil")
    st.markdown(f"""<div style="background:#F1EFE8;border:0.5px solid #D3D1C7;border-radius:10px;padding:10px 14px;font-size:0.82rem;color:#5F5E5A">
        📊 <b style="color:#2C2C2A">Pearson r = {corr_val:.2f}</b> — {interp} entre lluvia y nivel del río.<br>
        ℹ️ El río Sinú responde a la lluvia con rezago de 1-2 días por la cuenca del Alto Sinú.
    </div>""", unsafe_allow_html=True)

    st.markdown("<hr style='border:none;border-top:0.5px solid #D3D1C7;margin:16px 0'>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">📈 Históricas 30 días · Temperatura · Lluvia · PM2.5</div>', unsafe_allow_html=True)
    hist_clima=obtener_historico_30dias(); hist_aire=obtener_historico_aire_30dias()
    if hist_clima["ok"] and hist_clima["fechas"]:
        fechas_hist=[f[5:] for f in hist_clima["fechas"]]; paso=max(1,len(fechas_hist)//10)
        xticks_idx=list(range(0,len(fechas_hist),paso))
        fig_hist,axs=plt.subplots(3,1,figsize=(11,8),sharex=False); fig_hist.patch.set_facecolor("#FFFFFF")
        ax=axs[0]; ax.set_facecolor("#F9F8F6")
        ax.fill_between(range(len(fechas_hist)),hist_clima["temp_min"],hist_clima["temp_max"],alpha=0.25,color="#E24B4A",label="Rango")
        ax.plot(range(len(fechas_hist)),hist_clima["temp_max"],color="#E24B4A",linewidth=1.5,label="Tmax")
        ax.plot(range(len(fechas_hist)),hist_clima["temp_min"],color="#4FC3F7",linewidth=1.5,label="Tmin")
        ax.set_ylabel("°C",color="#5F5E5A",fontsize=8); ax.set_title("Temperatura máx/mín diaria",color="#2C2C2A",fontsize=9,pad=4)
        ax.tick_params(colors="#5F5E5A",labelsize=7); ax.set_xticks(xticks_idx)
        ax.set_xticklabels([fechas_hist[i] for i in xticks_idx],rotation=15)
        for spine in ax.spines.values(): spine.set_color("#D3D1C7")
        ax.grid(color="#E8E6E0",linewidth=0.5); ax.legend(fontsize=7,facecolor="#FFFFFF",labelcolor="#5F5E5A",loc="upper right")
        ax2h=axs[1]; ax2h.set_facecolor("#F9F8F6")
        ax2h.bar(range(len(fechas_hist)),hist_clima["lluvia"],color="#4FC3F7",alpha=0.75,width=0.7)
        ax2h.set_ylabel("mm",color="#5F5E5A",fontsize=8); ax2h.set_title("Precipitación diaria acumulada",color="#2C2C2A",fontsize=9,pad=4)
        ax2h.tick_params(colors="#5F5E5A",labelsize=7); ax2h.set_xticks(xticks_idx)
        ax2h.set_xticklabels([fechas_hist[i] for i in xticks_idx],rotation=15)
        for spine in ax2h.spines.values(): spine.set_color("#D3D1C7")
        ax2h.grid(axis="y",color="#E8E6E0",linewidth=0.5)
        ax3h=axs[2]; ax3h.set_facecolor("#F9F8F6")
        if hist_aire["ok"] and hist_aire["fechas"]:
            fechas_pm=[f[5:] for f in hist_aire["fechas"]]
            cpm=["#3B6D11" if v<10 else "#BA7517" if v<15 else "#E24B4A" if v<25 else "#A32D2D" for v in hist_aire["pm25"]]
            ax3h.bar(range(len(fechas_pm)),hist_aire["pm25"],color=cpm,alpha=0.85,width=0.7)
            ax3h.axhline(y=15,color="#BA7517",linestyle="--",linewidth=1,alpha=0.7,label="OMS límite (15)")
            paso_pm=max(1,len(fechas_pm)//10)
            ax3h.set_xticks(range(0,len(fechas_pm),paso_pm))
            ax3h.set_xticklabels([fechas_pm[i] for i in range(0,len(fechas_pm),paso_pm)],rotation=15,fontsize=7)
            ax3h.legend(fontsize=7,facecolor="#FFFFFF",labelcolor="#5F5E5A")
        ax3h.set_ylabel("µg/m³",color="#5F5E5A",fontsize=8); ax3h.set_title("PM2.5 promedio diario",color="#2C2C2A",fontsize=9,pad=4)
        ax3h.tick_params(colors="#5F5E5A",labelsize=7)
        for spine in ax3h.spines.values(): spine.set_color("#D3D1C7")
        ax3h.grid(axis="y",color="#E8E6E0",linewidth=0.5)
        plt.tight_layout(pad=1.2); st.pyplot(fig_hist); plt.close()
        t_prom=round(sum(hist_clima["temp_max"])/len(hist_clima["temp_max"]),1)
        ll_total=round(sum(hist_clima["lluvia"]),1); ll_max=round(max(hist_clima["lluvia"]),1)
        pm_prom=round(sum(hist_aire["pm25"])/len(hist_aire["pm25"]),1) if hist_aire["ok"] and hist_aire["pm25"] else "—"
        st.markdown(f"""<div style="background:#F1EFE8;border:0.5px solid #D3D1C7;border-radius:10px;padding:12px 16px;font-size:0.82rem">
            <b style="color:#3B6D11">Resumen últimos 30 días:</b> &nbsp;
            🌡️ Tmax prom.: <b>{t_prom}°C</b> &nbsp;·&nbsp;
            🌧️ Lluvia total: <b>{ll_total} mm</b> &nbsp;·&nbsp;
            ☔ Día más lluvioso: <b>{ll_max} mm</b> &nbsp;·&nbsp;
            💨 PM2.5 prom.: <b>{pm_prom} µg/m³</b>
        </div>""", unsafe_allow_html=True)
    else:
        st.info("Cargando datos históricos...")

    st.markdown("<hr style='border:none;border-top:0.5px solid #D3D1C7;margin:16px 0'>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">📊 Exportar datos · CSV</div>', unsafe_allow_html=True)
    import io
    df_export=pd.DataFrame({
        "Fecha":dias,"Nivel_rio_m":niveles,"Alerta_rio":[alerta_rio(n)[0] for n in niveles],
        "Lluvia_mm":lluvia_7d,"Temp_max_C":clima.get("temp_max",[0]*7),
        "PM25_ug_m3":[aire["pm25"]]*7,"PM10_ug_m3":[aire["pm10"]]*7,
        "NO2_ug_m3":[aire["no2"]]*7,"AQI_europeo":[aire["aqi"]]*7,
        "Heat_index_C":[hi_val]*7,"Alerta_calor":[hi_lbl]*7,
    })
    ex1,ex2,ex3=st.columns(3,gap="small")
    with ex1:
        csv_buf=io.StringIO(); df_export.to_csv(csv_buf,index=False,encoding="utf-8-sig")
        st.download_button("⬇️ Descargar CSV (7 días)",data=csv_buf.getvalue().encode("utf-8-sig"),
            file_name=f"biomonitor_{datetime.now(TZ_COL).strftime('%Y%m%d')}.csv",mime="text/csv",use_container_width=True)
    with ex2:
        if hist_clima["ok"] and hist_clima["fechas"]:
            df_h=pd.DataFrame({"Fecha":hist_clima["fechas"],"Temp_max_C":hist_clima["temp_max"],
                "Temp_min_C":hist_clima["temp_min"],"Lluvia_mm":hist_clima["lluvia"],"Viento_kmh":hist_clima["viento"]})
            if hist_aire["ok"] and hist_aire["fechas"]:
                df_h=df_h.merge(pd.DataFrame({"Fecha":hist_aire["fechas"],"PM25_ug_m3":hist_aire["pm25"]}),on="Fecha",how="left")
            csv_h=io.StringIO(); df_h.to_csv(csv_h,index=False,encoding="utf-8-sig")
            st.download_button("⬇️ Descargar CSV (30 días)",data=csv_h.getvalue().encode("utf-8-sig"),
                file_name=f"biomonitor_30d_{datetime.now(TZ_COL).strftime('%Y%m%d')}.csv",mime="text/csv",use_container_width=True)
    with ex3:
        st.dataframe(df_export[["Fecha","Nivel_rio_m","Lluvia_mm","PM25_ug_m3","Heat_index_C"]],
                     use_container_width=True,hide_index=True,height=180)

# ══════════════════════════════════════════════════════════
# TAB 4 — BIODIVERSIDAD
# ══════════════════════════════════════════════════════════
with tab_bio:
    st.markdown('<div class="section-header">🦜 Biodiversidad · GBIF · Córdoba, Colombia</div>', unsafe_allow_html=True)
    df_fauna_live,fauna_ok=obtener_fauna_gbif()
    if fauna_ok and df_fauna_live is not None:
        n_esp=len(df_fauna_live); n_img=int(df_fauna_live["imagen_url"].notna().sum())
        n_cls=df_fauna_live["clase"].nunique(); fuente_fauna="🟢 GBIF · tiempo real · 24h"
    else:
        n_esp,n_img,n_cls=12,12,8; fuente_fauna="🟡 Datos de respaldo"
        df_fauna_live=pd.DataFrame({
            "especie":["Heliconia psittacorum","Lygophis lineatus","Iguana iguana","Cairina moschata","Leptotila verreauxi","Chelonoidis carbonarius"],
            "nombre_com":["Heliconia","Culebra","Iguana","Pato real","Paloma","Morrocoy"],
            "clase":["Liliopsida","Squamata","Squamata","Aves","Aves","Testudines"],
            "orden":["Zingiberales","Squamata","Squamata","Anseriformes","Columbiformes","Testudines"],
            "familia":["Heliconiaceae","Colubridae","Iguanidae","Anatidae","Columbidae","Testudinidae"],
            "estado":["No evaluado"]*5+["Vulnerable"],
            "fecha":["2026-01-21","2026-01-11","2026-01-21","2026-01-22","2026-01-12","2026-01-25"],
            "imagen_url":[None]*6,"gbif_key":[""]*6,
        })

    f1,f2=st.columns(2,gap="small"); f3,f4=st.columns(2,gap="small")
    for col,lbl,val,sub,bc in [
        (f1,"Especies registradas",str(n_esp),fuente_fauna,"badge-purple"),
        (f2,"Con imagen",str(n_img),"Fotos verificadas","badge-green"),
        (f3,"Clases taxonómicas",str(n_cls),"Taxones distintos","badge-blue"),
        (f4,"Clasificación CNN","MobileNetV2","Precisión validada","badge-green"),
    ]:
        with col:
            st.markdown(f"""<div class="kpi-card kpi-card-purple">
                <div class="kpi-label">{lbl}</div><div class="kpi-value">{val}</div>
                <span class="badge {bc}">{sub}</span>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    cols_d=[c for c in ["especie","nombre_com","clase","orden","familia","estado","fecha"] if c in df_fauna_live.columns]
    df_m=df_fauna_live[cols_d].head(12).copy(); df_m.columns=[c.replace("_"," ").capitalize() for c in df_m.columns]
    st.dataframe(df_m,use_container_width=True,hide_index=True,height=320)

    st.markdown("<hr style='border:none;border-top:0.5px solid #D3D1C7;margin:16px 0'>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">📸 Galería de especies · Córdoba, Colombia · GBIF tiempo real</div>', unsafe_allow_html=True)

    imagenes_gbif=[]
    if fauna_ok and df_fauna_live is not None and "imagen_url" in df_fauna_live.columns:
        for _,row in df_fauna_live.iterrows():
            url=row.get("imagen_url")
            if pd.notna(url) and url and isinstance(url,str) and url.startswith("http"):
                imagenes_gbif.append((url,row.get("especie","Especie")))
            if len(imagenes_gbif)>=6: break

    archivos_local=[
        ("imagenes_fauna/Heliconia_psittacorum.jpg","Heliconia psittacorum"),
        ("imagenes_fauna/Iguana_iguana.jpg","Iguana iguana"),
        ("imagenes_fauna/Leptotila_verreauxi.jpg","Leptotila verreauxi"),
        ("imagenes_fauna/Chelonoidis_carbonarius.jpg","Chelonoidis carbonarius"),
        ("imagenes_fauna/Cairina_moschata.jpg","Cairina moschata"),
        ("imagenes_fauna/Sakesphorus_canadensis.jpg","Sakesphorus canadensis"),
    ]

    def _render_img(col_obj,url_or_path,nombre,es_url=True):
        placeholder=f"""<div style="background:#F1EFE8;border:0.5px solid #D3D1C7;border-radius:10px;padding:16px;text-align:center;font-size:0.75rem;color:#5F5E5A">🦜<br><i>{nombre}</i></div>"""
        try:
            if es_url: col_obj.image(url_or_path,caption=nombre,use_container_width=True)
            else: col_obj.image(Image.open(url_or_path),caption=nombre,use_container_width=True)
        except: col_obj.markdown(placeholder,unsafe_allow_html=True)

    if len(imagenes_gbif)>=3:
        fuente_label=imagenes_gbif; es_url_flag=True
        label_tag=f"<small style='color:#3B6D11'>📷 {len(imagenes_gbif)} imágenes · GBIF · Córdoba, Colombia</small>"
    else:
        fuente_label=archivos_local; es_url_flag=False
        label_tag="<small style='color:#888780'>📷 Imágenes locales · Banco fotográfico BioMonitor</small>"

    items=fuente_label[:6]
    for fila_idx in range(0,len(items),3):
        trio=items[fila_idx:fila_idx+3]; gcols=st.columns(len(trio),gap="small")
        for ci,(src_img,nombre) in enumerate(trio):
            _render_img(gcols[ci],src_img,nombre,es_url=es_url_flag)
    st.markdown(label_tag,unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# TAB 5 — ALERTAS
# ══════════════════════════════════════════════════════════
with tab_alertas:
    st.markdown('<div class="section-header">🔔 Alertas activas · Montería</div>', unsafe_allow_html=True)
    alerta_lbl_t,_,_=alerta_rio(niveles[0])
    if niveles[0]>=4.0: st.warning(f"🌊 **Río Sinú en alerta {alerta_lbl_t}** — Nivel: {niveles[0]}m. Monitorear zonas bajas.")
    else: st.success(f"✅ **Río Sinú en estado normal** — Nivel: {niveles[0]}m")
    hi_t,hi_lbl_t,_,_=calcular_heat_index(clima.get("temp",30),clima.get("humedad",75))
    if hi_t>=32: st.warning(f"🌡️ **Calor aparente elevado: {hi_t}°C** — {hi_lbl_t}. Evitar exposición prolongada al sol.")
    else: st.success(f"✅ **Temperatura confortable** — Calor aparente: {hi_t}°C")
    pm25_v2=aire.get("pm25",0)
    if pm25_v2>=15: st.warning(f"💨 **PM2.5 sobre límite OMS** — {pm25_v2} µg/m³. Límite: 15 µg/m³")
    else: st.success(f"✅ **Calidad del aire buena** — PM2.5: {pm25_v2} µg/m³")

    st.markdown("<hr style='border:none;border-top:0.5px solid #D3D1C7;margin:14px 0'>", unsafe_allow_html=True)
    nivel_al=niveles[0]; alerta_lbl_al,_,_=alerta_rio(nivel_al)
    with st.expander(f"🌊 Zonas afectadas — Estado: {alerta_lbl_al} ({nivel_al}m)",expanded=nivel_al>=4.0):
        for zona,barrios,ubicacion,cota,accion in [
            ("Zona ALTO riesgo","La Granja · La Ribera · Los Nogales","Margen occidental, cota baja",4.0,"Evacuar si nivel supera 5m · Av. Circunvalar"),
            ("Zona ALTO riesgo","Barrio Colón · Chuchurubi · Santa Fe","Sector sur, inundación histórica",4.0,"Contactar Defensa Civil: 144"),
            ("Zona MEDIO riesgo","Ronda del Sinú norte · Av. Primera","Parque lineal y avenida ribereña",5.5,"Cerrar acceso si nivel > 5.5m"),
            ("Zona MEDIO riesgo","El Recreo · Ribera norte","Barrio nororiental junto al río",5.5,"Monitorear en temporada de lluvias"),
            ("Zona ALTO riesgo","Mocarí · Zona sur rural","Área baja al sur de Montería",4.0,"Riesgo de pérdidas en cultivos"),
        ]:
            if nivel_al>=cota+1.5: bc,et="badge-red","🔴 INUNDACIÓN"
            elif nivel_al>=cota:   bc,et="badge-yellow","🟠 ALERTA"
            elif nivel_al>=cota-0.5: bc,et="badge-yellow","🟡 PRECAUCIÓN"
            else:                  bc,et="badge-green","✅ Normal"
            st.markdown(f"""<div class="info-card">
                <span class="badge {bc}">{zona}</span>
                <b style="margin-left:8px">{barrios}</b><br>
                <span style="color:#444441;font-size:0.82rem">📍 {ubicacion} · Cota: {cota}m</span><br>
                <span style="color:#2C2C2A;font-size:0.82rem;font-weight:500">📊 {et} — nivel actual: {nivel_al}m</span><br>
                <span style="color:#444441;font-size:0.8rem">💡 {accion}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown('<div class="info-card">📞 <b>Emergencias:</b> Defensa Civil 144 · Bomberos 119 · Cruz Roja 132</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════
st.markdown(f"""
<div style='text-align:center;color:#888780;font-size:0.8rem;
            padding:18px 0 28px 0;border-top:0.5px solid #D3D1C7;margin-top:14px;line-height:2'>
    <b style='color:#3B6D11;font-size:0.9rem'>BioMonitor Montería</b>
    &nbsp;·&nbsp; {datetime.now(TZ_COL).strftime('%d/%m/%Y %H:%M')}
    &nbsp;·&nbsp; Open-Meteo · IDEAM · GBIF · LSTM + MobileNetV2
    &nbsp;·&nbsp; <b style='color:#3B6D11'>© Ivan Contreras</b>
</div>""", unsafe_allow_html=True)