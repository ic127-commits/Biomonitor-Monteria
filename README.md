# 🌿 BioMonitor Montería

Plataforma inteligente de monitoreo ambiental en tiempo real para **Montería, Córdoba, Colombia**.

## 🚀 Demo en vivo
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://biomonitor-monteria.streamlit.app)

## 📡 Módulos

| Módulo | Fuente | Actualización |
|--------|--------|---------------|
| 🌊 Río Sinú — nivel + predicción 7 días (LSTM) | IDEAM / datos.gov.co | 30 min |
| 🌡️ Clima — temperatura, humedad, lluvia, viento | Open-Meteo | 30 min |
| 💨 Calidad del aire — PM2.5, PM10, NO₂, AQI | Open-Meteo Air Quality | 30 min |
| 🦜 Biodiversidad — especies con imagen y nombre común | GBIF | 24 h |
| 🔍 Buscador de lugares con clima en tiempo real | Nominatim + Open-Meteo | Tiempo real |

## 🗂️ Estructura

```
proyecto_monteria/
├── dashboard.py          # App principal
├── requirements.txt      # Dependencias
├── Biomotorlogo.png      # Logo de la app
└── imagenes_fauna/       # Fotos locales de respaldo
    ├── Heliconia_psittacorum.jpg
    ├── Iguana_iguana.jpg
    ├── Leptotila_verreauxi.jpg
    ├── Chelonoidis_carbonarius.jpg
    ├── Cairina_moschata.jpg
    └── Sakesphorus_canadensis.jpg
```

## 🛠️ Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

## 🌐 Despliegue en Streamlit Cloud

1. Sube el repositorio a GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta el repo y selecciona `dashboard.py`
4. ¡Listo!

## 📊 Tecnologías

- **Streamlit** — interfaz web
- **Folium** — mapa interactivo
- **LSTM** — predicción de niveles del río
- **MobileNetV2 (CNN)** — clasificación de fauna
- **Open-Meteo API** — datos meteorológicos
- **GBIF API** — registros de biodiversidad
- **IDEAM / datos.gov.co** — hidrología oficial

## 👤 Autor

**© Ivan Contreras** — Montería, Córdoba, Colombia
