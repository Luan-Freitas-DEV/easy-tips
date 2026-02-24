from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr

from app.models.models import OfferKind, OfferStatus, ServiceStatus, UserRole


class RegisterIn(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole

    class Config:
        from_attributes = True


class ServiceIn(BaseModel):
    title: str
    description: str
    service_type: str
    origin_address: str
    origin_lat: float
    origin_lng: float
    dest_address: str
    dest_lat: float
    dest_lng: float
    pickup_window_start: datetime
    pickup_window_end: datetime
    delivery_window_start: datetime
    delivery_window_end: datetime
    offered_price: float


class ServicePatch(BaseModel):
    title: str | None = None
    description: str | None = None
    offered_price: float | None = None


class ServiceOut(ServiceIn):
    id: int
    created_by_user_id: int
    status: ServiceStatus

    class Config:
        from_attributes = True


class OfferIn(BaseModel):
    kind: OfferKind
    price: float
    message: str | None = None


class OfferOut(BaseModel):
    id: int
    service_id: int
    driver_user_id: int
    kind: OfferKind
    price: float
    message: str | None
    status: OfferStatus

    class Config:
        from_attributes = True


class DriverIntentIn(BaseModel):
    current_lat: float | None = None
    current_lng: float | None = None
    intended_dest_lat: float
    intended_dest_lng: float
    intended_dest_address: str
    available_from: datetime
    available_to: datetime


class BackhaulOut(BaseModel):
    service_id: int
    title: str
    offered_price: float
    pickup_distance_km: float
    detour_distance_km: float
    origin_to_dest_km: float
    score: float


class StatusActionIn(BaseModel):
    reason: str | None = None


RoleLiteral = Literal["SHIPPER", "DRIVER", "BOTH"]
