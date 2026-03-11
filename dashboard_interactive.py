#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from pathlib import Path

# ==============================
# CONFIGURACIÓN
# ==============================
st.set_page_config(
    page_title="Dashboard Interactivo",
    page_icon="🎛️",
    layout="wide"
)

st.title("🎛️ Dashboard Interactivo - OpenWeather ETL")

# ==============================
# CARGAR DATOS DESDE CSV
# ==============================
CSV_PATH = Path("data/clima.csv")

if not CSV_PATH.exists():
    st.error("❌ No se encontró el archivo data/clima.csv en el repositorio.")
    st.stop()

df = pd.read_csv(CSV_PATH)

if df.empty:
    st.warning("⚠️ El CSV no contiene datos.")
    st.stop()

# ==============================
# NORMALIZAR COLUMNAS (por si cambian acentos)
# ==============================
rename_map = {
    "Pais": "País",
    "Sensacion": "Sensación",
    "Sensacion_termica": "Sensación",
    "Descripcion": "Descripción",
    "Velocidad_viento": "Viento",
    "Presion": "Presion",
    "fecha_extraccion": "Fecha",
    "ciudad": "Ciudad",
    "pais": "País",
    "temperatura": "Temperatura",
    "humedad": "Humedad",
    "velocidad_viento": "Viento",
    "presion": "Presion",
    "descripcion": "Descripción",
}
for k, v in rename_map.items():
    if k in df.columns and v not in df.columns:
        df.rename(columns={k: v}, inplace=True)

# Validar columnas mínimas
required_cols = ["Ciudad", "Temperatura", "Humedad", "Descripción", "Fecha"]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"❌ Faltan columnas en el CSV: {missing}")
    st.stop()

# ==============================
# LIMPIEZA Y PREPARACIÓN
# ==============================
df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
df = df.dropna(subset=['Fecha'])

# ==============================
# SIDEBAR - FILTROS
# ==============================
st.sidebar.markdown("### 🔧 Controles")

ciudades_disponibles = sorted(df['Ciudad'].dropna().unique())

ciudades_seleccionadas = st.sidebar.multiselect(
    "🏙️ Ciudades a Mostrar",
    options=ciudades_disponibles,
    default=ciudades_disponibles
)

fecha_min = df['Fecha'].min().date()
fecha_max = df['Fecha'].max().date()

col1, col2 = st.sidebar.columns(2)

with col1:
    fecha_inicio = st.date_input(
        "📅 Desde:",
        value=fecha_min,
        min_value=fecha_min,
        max_value=fecha_max
    )

with col2:
    fecha_fin = st.date_input(
        "📅 Hasta:",
        value=fecha_max,
        min_value=fecha_min,
        max_value=fecha_max
    )

temp_min, temp_max = st.sidebar.slider(
    "🌡️ Rango de Temperatura (°C)",
    min_value=-50,
    max_value=50,
    value=(-10, 40)
)

# ==============================
# FILTRAR DATAFRAME
# ==============================
fecha_inicio_dt = pd.to_datetime(fecha_inicio)
fecha_fin_dt = pd.to_datetime(fecha_fin) + pd.Timedelta(days=1)

df_filtrado = df[
    (df['Ciudad'].isin(ciudades_seleccionadas)) &
    (df['Fecha'] >= fecha_inicio_dt) &
    (df['Fecha'] < fecha_fin_dt) &
    (df['Temperatura'] >= temp_min) &
    (df['Temperatura'] <= temp_max)
]

st.write("Fecha mínima en datos:", df['Fecha'].min())
st.write("Fecha máxima en datos:", df['Fecha'].max())

# ==============================
# CONTENIDO PRINCIPAL
# ==============================
if not df_filtrado.empty:

    st.markdown("### 📊 Indicadores Clave")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("🌡️ Temp Max", f"{df_filtrado['Temperatura'].max():.1f}°C")

    with col2:
        st.metric("🌡️ Temp Min", f"{df_filtrado['Temperatura'].min():.1f}°C")

    with col3:
        st.metric("🌡️ Temp Prom", f"{df_filtrado['Temperatura'].mean():.1f}°C")

    with col4:
        st.metric("💧 Humedad Prom", f"{df_filtrado['Humedad'].mean():.1f}%")

    with col5:
        viento_col = 'Viento' if 'Viento' in df_filtrado.columns else None
        if viento_col:
            st.metric("💨 Viento Max", f"{df_filtrado[viento_col].max():.1f} m/s")
        else:
            st.metric("💨 Viento Max", "N/A")

    st.markdown("---")

    # ==============================
    # GRÁFICAS
    # ==============================
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📦 Distribución de Temperaturas")
        fig = px.box(
            df_filtrado,
            x='Ciudad',
            y='Temperatura',
            color='Ciudad'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 💧 Promedio de Humedad")
        humedad_ciudad = df_filtrado.groupby('Ciudad')['Humedad'].mean().reset_index()
        fig = px.bar(
            humedad_ciudad,
            x='Ciudad',
            y='Humedad',
            color='Humedad',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ==============================
    # EVOLUCIÓN TEMPORAL
    # ==============================
    st.markdown("#### 📈 Evolución Temporal")

    temp_tiempo = df_filtrado.groupby(
        ['Fecha', 'Ciudad']
    )['Temperatura'].mean().reset_index()

    fig = px.line(
        temp_tiempo,
        x='Fecha',
        y='Temperatura',
        color='Ciudad',
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ==============================
    # TABLA INTERACTIVA
    # ==============================
    st.markdown("#### 📋 Datos Detallados")

    col1, col2 = st.columns(2)

    with col1:
        mostrar_todos = st.checkbox("Mostrar todos los registros", value=False)

    with col2:
        columnas_mostrar = st.multiselect(
            "Columnas a mostrar:",
            df_filtrado.columns.tolist(),
            default=[c for c in ['Ciudad', 'Temperatura', 'Humedad', 'Descripción', 'Fecha'] if c in df_filtrado.columns]
        )

    if mostrar_todos:
        st.dataframe(df_filtrado[columnas_mostrar],
                     use_container_width=True,
                     height=600)
    else:
        st.dataframe(df_filtrado[columnas_mostrar].head(20),
                     use_container_width=True)

    # ==============================
    # DESCARGA CSV
    # ==============================
    st.markdown("---")

    csv = df_filtrado.to_csv(index=False)

    st.download_button(
        label="⬇️ Descargar datos como CSV",
        data=csv,
        file_name=f"clima_datos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

else:
    st.warning("⚠️ No hay datos que coincidan con los filtros seleccionados")