#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import plotly.express as px
import sys

sys.path.insert(0, '.')

from scripts.database import SessionLocal
from scripts.models import Clima


# ==============================
# Configuración de página
# ==============================
st.set_page_config(
    page_title="Dashboard Clima ETL",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌍 Dashboard de Clima - OpenWeather ETL")
st.markdown("---")


# ==============================
# Función para cargar datos
# ==============================
@st.cache_data
def cargar_datos():

    db = SessionLocal()

    try:

        registros = db.query(Clima).order_by(
            Clima.fecha_extraccion.desc()
        ).all()

        data = []

        for r in registros:
            data.append({
                "Ciudad": r.ciudad,
                "País": r.pais,
                "Temperatura": r.temperatura,
                "Sensación Térmica": r.sensacion_termica,
                "Humedad": r.humedad,
                "Presión": r.presion,
                "Viento": r.velocidad_viento,
                "Descripción": r.descripcion,
                "Fecha": r.fecha_extraccion
            })

        df = pd.DataFrame(data)

        return df

    finally:
        db.close()


# ==============================
# Cargar datos
# ==============================
df = cargar_datos()

if df.empty:
    st.warning("⚠️ No hay datos en la base de datos.")
    st.stop()


# ==============================
# SIDEBAR
# ==============================
st.sidebar.title("🔎 Filtros")

ciudades = st.sidebar.multiselect(
    "Selecciona Ciudades:",
    options=df["Ciudad"].unique(),
    default=df["Ciudad"].unique()
)

df_filtrado = df[df["Ciudad"].isin(ciudades)]


# ==============================
# MÉTRICAS PRINCIPALES
# ==============================
st.subheader("📊 Métricas Principales")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "🌡️ Temp. Promedio",
        f"{df_filtrado['Temperatura'].mean():.1f} °C"
    )

with col2:
    st.metric(
        "💧 Humedad Promedio",
        f"{df_filtrado['Humedad'].mean():.1f} %"
    )

with col3:
    st.metric(
        "💨 Viento Máximo",
        f"{df_filtrado['Viento'].max():.1f} m/s"
    )

with col4:
    st.metric(
        "📈 Total Registros",
        len(df_filtrado)
    )

st.markdown("---")


# ==============================
# VISUALIZACIONES
# ==============================
st.subheader("📉 Visualizaciones")

col1, col2 = st.columns(2)


# Temperatura promedio por ciudad
with col1:

    temp_ciudad = df_filtrado.groupby("Ciudad")["Temperatura"].mean().reset_index()

    fig_temp = px.bar(
        temp_ciudad.sort_values("Temperatura", ascending=False),
        x="Ciudad",
        y="Temperatura",
        title="Temperatura Promedio por Ciudad",
        color="Temperatura",
        color_continuous_scale="RdYlBu_r"
    )

    st.plotly_chart(fig_temp, use_container_width=True)


# Humedad promedio por ciudad
with col2:

    hum_ciudad = df_filtrado.groupby("Ciudad")["Humedad"].mean().reset_index()

    fig_hum = px.bar(
        hum_ciudad,
        x="Ciudad",
        y="Humedad",
        title="Humedad Promedio por Ciudad",
        color="Humedad",
        color_continuous_scale="Blues"
    )

    st.plotly_chart(fig_hum, use_container_width=True)


# ==============================
# Scatter
# ==============================
col1, col2 = st.columns(2)

with col1:

    fig_scatter = px.scatter(
        df_filtrado,
        x="Temperatura",
        y="Humedad",
        size="Viento",
        color="Ciudad",
        hover_data=["Descripción"],
        title="Temperatura vs Humedad"
    )

    st.plotly_chart(fig_scatter, use_container_width=True)


# Evolución temporal
with col2:

    df_time = df_filtrado.sort_values("Fecha")

    fig_line = px.line(
        df_time,
        x="Fecha",
        y="Temperatura",
        color="Ciudad",
        title="Evolución de Temperatura"
    )

    st.plotly_chart(fig_line, use_container_width=True)


st.markdown("---")


# ==============================
# TABLA DETALLADA
# ==============================
st.subheader("📋 Datos Detallados")

st.dataframe(
    df_filtrado.sort_values("Fecha", ascending=False),
    use_container_width=True,
    height=400
)