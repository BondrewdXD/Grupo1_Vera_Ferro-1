#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from scripts.database import SessionLocal
from scripts.models import Clima
from sqlalchemy import func
import pandas as pd

db = SessionLocal()


def temperatura_promedio_por_ciudad():
    """Temperatura promedio de cada ciudad"""

    registros = db.query(
        Clima.ciudad,
        func.avg(Clima.temperatura).label('temp_promedio')
    ).group_by(Clima.ciudad).all()

    if registros:
        df = pd.DataFrame(registros, columns=['Ciudad', 'Temperatura Promedio'])
        print("\n📊 TEMPERATURA PROMEDIO POR CIUDAD:")
        print(df.to_string(index=False))
    else:
        print("\n⚠️ No hay datos registrados.")


def ciudad_mas_humeda():
    """Ciudad con mayor humedad registrada"""

    registro = db.query(
        Clima.ciudad,
        Clima.humedad,
        Clima.fecha_extraccion
    ).order_by(
        Clima.humedad.desc()
    ).first()

    if registro:
        print(f"\n💧 CIUDAD MÁS HÚMEDA:")
        print(f"   {registro.ciudad} con {registro.humedad}% "
              f"(Fecha: {registro.fecha_extraccion})")
    else:
        print("\n⚠️ No hay datos registrados.")


def velocidad_viento_max():
    """Mayor velocidad de viento registrada"""

    registro = db.query(
        Clima.ciudad,
        Clima.velocidad_viento,
        Clima.fecha_extraccion
    ).order_by(
        Clima.velocidad_viento.desc()
    ).first()

    if registro:
        print(f"\n💨 VIENTO MÁS FUERTE:")
        print(f"   {registro.ciudad} con {registro.velocidad_viento} m/s "
              f"(Fecha: {registro.fecha_extraccion})")
    else:
        print("\n⚠️ No hay datos registrados.")


def temperatura_maxima():
    """Temperatura más alta registrada"""

    registro = db.query(
        Clima.ciudad,
        Clima.temperatura,
        Clima.fecha_extraccion
    ).order_by(
        Clima.temperatura.desc()
    ).first()

    if registro:
        print(f"\n🔥 TEMPERATURA MÁS ALTA:")
        print(f"   {registro.ciudad} con {registro.temperatura}°C "
              f"(Fecha: {registro.fecha_extraccion})")


def temperatura_minima():
    """Temperatura más baja registrada"""

    registro = db.query(
        Clima.ciudad,
        Clima.temperatura,
        Clima.fecha_extraccion
    ).order_by(
        Clima.temperatura.asc()
    ).first()

    if registro:
        print(f"\n❄️ TEMPERATURA MÁS BAJA:")
        print(f"   {registro.ciudad} con {registro.temperatura}°C "
              f"(Fecha: {registro.fecha_extraccion})")


if __name__ == "__main__":
    try:
        print("\n" + "=" * 50)
        print("ANÁLISIS DE DATOS - POSTGRESQL")
        print("=" * 50)

        temperatura_promedio_por_ciudad()
        ciudad_mas_humeda()
        velocidad_viento_max()
        temperatura_maxima()
        temperatura_minima()

        print("\n" + "=" * 50 + "\n")

    finally:
        db.close()