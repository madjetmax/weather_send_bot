from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped, mapped_column,
    relationship
)
from sqlalchemy import (
    Integer, String, Float,
    Boolean, ForeignKey,
    JSON, Table, Column,
    DateTime, BigInteger
)
from sqlalchemy import func
from datetime import datetime, UTC
from typing import Optional
from enum import Enum

def get_now():
    return datetime.now(UTC).replace(tzinfo=None)

class Base(DeclarativeBase):
    created_at: Mapped[datetime]= mapped_column(
        default=get_now, 
        server_default=func.now()
    )
    updated_at: Mapped[datetime]= mapped_column(
        default=get_now, onupdate=get_now, 
        server_default=func.now(), server_onupdate=func.now()
    )

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)

    # location
    lat: Mapped[float] = mapped_column(Float, nullable=True)
    long: Mapped[float] = mapped_column(Float, nullable=True)


class WeatherLog(Base):
    __tablename__ = "weather_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    date: Mapped[datetime]
    name: Mapped[str] = mapped_column(String(128))

    # temperature
    temperature: Mapped[float]
    temp_feels_like: Mapped[float]
    max_temp: Mapped[float]
    min_temp: Mapped[float]

    wind_speed: Mapped[float]

    # other
    humidity: Mapped[float]    
    visibility: Mapped[int]

    # location
    lat: Mapped[float]
    long: Mapped[float]