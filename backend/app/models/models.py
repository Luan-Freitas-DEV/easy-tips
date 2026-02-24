from datetime import datetime
from enum import Enum

from sqlalchemy import (
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class UserRole(str, Enum):
    SHIPPER = "SHIPPER"
    DRIVER = "DRIVER"
    BOTH = "BOTH"


class ServiceStatus(str, Enum):
    PUBLICADO = "PUBLICADO"
    EM_NEGOCIACAO = "EM_NEGOCIACAO"
    ACEITO = "ACEITO"
    COLETADO = "COLETADO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"


class OfferKind(str, Enum):
    ACCEPT = "ACCEPT"
    COUNTER = "COUNTER"


class OfferStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.SHIPPER)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DriverProfile(Base):
    __tablename__ = "driver_profiles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    vehicle_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    capacity_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    base_city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    base_state: Mapped[str | None] = mapped_column(String(2), nullable=True)


class ShipperProfile(Base):
    __tablename__ = "shipper_profiles"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    profile_type: Mapped[str] = mapped_column(String(10), default="PF")
    document_id: Mapped[str | None] = mapped_column(String(30), nullable=True)


class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text)
    service_type: Mapped[str] = mapped_column(String(80))
    origin_address: Mapped[str] = mapped_column(String(255))
    origin_lat: Mapped[float] = mapped_column(Float)
    origin_lng: Mapped[float] = mapped_column(Float)
    dest_address: Mapped[str] = mapped_column(String(255))
    dest_lat: Mapped[float] = mapped_column(Float)
    dest_lng: Mapped[float] = mapped_column(Float)
    pickup_window_start: Mapped[datetime] = mapped_column(DateTime)
    pickup_window_end: Mapped[datetime] = mapped_column(DateTime)
    delivery_window_start: Mapped[datetime] = mapped_column(DateTime)
    delivery_window_end: Mapped[datetime] = mapped_column(DateTime)
    offered_price: Mapped[float] = mapped_column(Numeric(12, 2))
    status: Mapped[ServiceStatus] = mapped_column(SAEnum(ServiceStatus), default=ServiceStatus.PUBLICADO)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    offers = relationship("Offer", back_populates="service")


class Offer(Base):
    __tablename__ = "offers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"), index=True)
    driver_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    kind: Mapped[OfferKind] = mapped_column(SAEnum(OfferKind))
    price: Mapped[float] = mapped_column(Numeric(12, 2))
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[OfferStatus] = mapped_column(SAEnum(OfferStatus), default=OfferStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    service = relationship("Service", back_populates="offers")


class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"), unique=True)
    driver_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    accepted_offer_id: Mapped[int] = mapped_column(ForeignKey("offers.id"))
    accepted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DriverIntent(Base):
    __tablename__ = "driver_intents"

    driver_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    current_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    intended_dest_lat: Mapped[float] = mapped_column(Float)
    intended_dest_lng: Mapped[float] = mapped_column(Float)
    intended_dest_address: Mapped[str] = mapped_column(String(255))
    available_from: Mapped[datetime] = mapped_column(DateTime)
    available_to: Mapped[datetime] = mapped_column(DateTime)
