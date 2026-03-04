from sqlalchemy import Column, Integer, String, Float, DateTime
from scripts.database import Base
from datetime import datetime

class Clima(Base):
    __tablename__ = "clima"

    id = Column(Integer, primary_key=True, index=True)

    ciudad = Column(String(100), nullable=False)
    pais = Column(String(100), nullable=False)

    latitud = Column(Float)
    longitud = Column(Float)

    temperatura = Column(Float)
    sensacion_termica = Column(Float)
    humedad = Column(Integer)
    presion = Column(Integer)

    velocidad_viento = Column(Float)
    descripcion = Column(String(255))

    fecha_extraccion = Column(DateTime, default=datetime.utcnow)