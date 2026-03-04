#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from sqlalchemy import func
import sys
sys.path.insert(0, '.')

from scripts.database import SessionLocal
from scripts.models import Clima

# ==============================
# CONFIGURACIÓN
# ==============================
st.set_page_config(
    page_title="Dashboard Avanzado Clima",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌍 Dashboard Avanzado - OpenWeather ETL")
st.markdown("---")

db = SessionLocal()

# ==============================
# CARGAR DATOS
# ==============================
registros = db.query(Clima).order_by(
    Clima.fecha_extraccion.desc()
).all()

data = []
for r in registros:
    data.append({
        "Ciudad": r.ciudad,
        "Pais": r.pais,
        "Temperatura": r.temperatura,
        "Humedad": r.humedad,
        "Viento": r.velocidad_viento,
        "Presion": r.presion,
        "Descripcion": r.descripcion,
        "Fecha": r.fecha_extraccion
    })

df = pd.DataFrame(data)

if df.empty:
    st.warning("⚠️ No hay datos en la base de datos.")
    st.stop()

# ==============================
# TABS
# ==============================
tab1, tab2, tab3 = st.tabs(
    ["📊 Vista General", "📈 Histórico", "🔍 Análisis Estadístico"]
)

# =====================================================
# TAB 1 - VISTA GENERAL
# =====================================================
with tab1:
    st.subheader("Resumen General")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🏙️ Ciudades", df["Ciudad"].nunique())

    with col2:
        st.metric("📊 Registros Totales", len(df))

    with col3:
        st.metric("🌡️ Temp Promedio",
                  f"{df['Temperatura'].mean():.1f} °C")

    with col4:
        ultima_fecha = df["Fecha"].max()
        st.metric("⏰ Última Actualización",
                  ultima_fecha.strftime("%Y-%m-%d %H:%M"))

    st.markdown("---")

    col1, col2 = st.columns(2)

    # Temperatura promedio por ciudad
    with col1:
        temp_ciudad = df.groupby("Ciudad")["Temperatura"].mean().reset_index()

        fig = px.bar(
            temp_ciudad,
            x="Ciudad",
            y="Temperatura",
            title="Temperatura Promedio por Ciudad",
            color="Temperatura",
            color_continuous_scale="RdYlBu_r"
        )
        st.plotly_chart(fig, use_container_width=True)

    # Humedad promedio
    with col2:
        hum_ciudad = df.groupby("Ciudad")["Humedad"].mean().reset_index()

        fig = px.bar(
            hum_ciudad,
            x="Ciudad",
            y="Humedad",
            title="Humedad Promedio por Ciudad",
            color="Humedad",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig, use_container_width=True)

# =====================================================
# TAB 2 - HISTÓRICO
# =====================================================
with tab2:
    st.subheader("Análisis Histórico")

    col1, col2 = st.columns(2)

    with col1:
        fecha_inicio = st.date_input(
            "Desde:",
            value=datetime.now() - timedelta(days=7)
        )

    with col2:
        fecha_fin = st.date_input(
            "Hasta:",
            value=datetime.now()
        )

    df_filtrado = df[
        (df["Fecha"] >= pd.to_datetime(fecha_inicio)) &
        (df["Fecha"] <= pd.to_datetime(fecha_fin))
    ]

    if not df_filtrado.empty:

        fig = px.line(
            df_filtrado.sort_values("Fecha"),
            x="Fecha",
            y="Temperatura",
            color="Ciudad",
            markers=True,
            title="Temperatura en el Tiempo"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        fig2 = px.line(
            df_filtrado.sort_values("Fecha"),
            x="Fecha",
            y="Humedad",
            color="Ciudad",
            markers=True,
            title="Humedad en el Tiempo"
        )

        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        st.dataframe(df_filtrado, use_container_width=True)

    else:
        st.warning("No hay datos en ese rango de fechas.")

# =====================================================
# TAB 3 - ANÁLISIS ESTADÍSTICO
# =====================================================
with tab3:
    st.subheader("Análisis Estadístico por Ciudad")

    ciudades = df["Ciudad"].unique()

    for ciudad in ciudades:
        with st.expander(f"📍 {ciudad}"):

            df_ciudad = df[df["Ciudad"] == ciudad]

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("🌡️ Temp Prom.",
                          f"{df_ciudad['Temperatura'].mean():.1f} °C")

            with col2:
                st.metric("🔥 Temp Máx.",
                          f"{df_ciudad['Temperatura'].max():.1f} °C")

            with col3:
                st.metric("❄️ Temp Mín.",
                          f"{df_ciudad['Temperatura'].min():.1f} °C")

            with col4:
                st.metric("💨 Viento Máx.",
                          f"{df_ciudad['Viento'].max():.1f} m/s")

            # Scatter adicional
            fig = px.scatter(
                df_ciudad,
                x="Temperatura",
                y="Humedad",
                size="Viento",
                color="Fecha",
                title=f"Relación Temp vs Humedad - {ciudad}"
            )

            st.plotly_chart(fig, use_container_width=True)

db.close()