from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core.config import settings
from app.core.db import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.models import (
    Assignment,
    DriverIntent,
    DriverProfile,
    Offer,
    OfferKind,
    OfferStatus,
    Service,
    ServiceStatus,
    ShipperProfile,
    User,
    UserRole,
)
from app.schemas.schemas import (
    BackhaulOut,
    DriverIntentIn,
    LoginIn,
    OfferIn,
    OfferOut,
    RegisterIn,
    ServiceIn,
    ServiceOut,
    ServicePatch,
    TokenOut,
    UserOut,
)
from app.services.geo import haversine_km

app = FastAPI(title="Easy Tips API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/auth/register", response_model=UserOut)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.flush()
    if payload.role in [UserRole.DRIVER, UserRole.BOTH]:
        db.add(DriverProfile(user_id=user.id))
    if payload.role in [UserRole.SHIPPER, UserRole.BOTH]:
        db.add(ShipperProfile(user_id=user.id, profile_type="PF"))
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    return TokenOut(access_token=create_access_token(str(user.id)))


@app.get("/me", response_model=UserOut)
def me(user: User = Depends(current_user)):
    return user


def require_shipper(user: User):
    if user.role not in [UserRole.SHIPPER, UserRole.BOTH]:
        raise HTTPException(status_code=403, detail="Apenas embarcador")


def require_driver(user: User):
    if user.role not in [UserRole.DRIVER, UserRole.BOTH]:
        raise HTTPException(status_code=403, detail="Apenas caminhoneiro")


@app.post("/services", response_model=ServiceOut)
def create_service(payload: ServiceIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    require_shipper(user)
    service = Service(created_by_user_id=user.id, **payload.model_dump())
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@app.get("/services", response_model=list[ServiceOut])
def list_services(
    near_lat: float | None = None,
    near_lng: float | None = None,
    radius_km: float = 100,
    status: ServiceStatus = ServiceStatus.PUBLICADO,
    db: Session = Depends(get_db),
):
    services = list(db.scalars(select(Service).where(Service.status == status)).all())
    if near_lat is not None and near_lng is not None:
        services = [
            s
            for s in services
            if haversine_km(near_lat, near_lng, s.origin_lat, s.origin_lng) <= radius_km
        ]
    return services


@app.get("/services/{service_id}", response_model=ServiceOut)
def get_service(service_id: int, db: Session = Depends(get_db)):
    service = db.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    return service


@app.patch("/services/{service_id}", response_model=ServiceOut)
def patch_service(
    service_id: int,
    payload: ServicePatch,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    service = db.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    if service.created_by_user_id != user.id:
        raise HTTPException(status_code=403, detail="Sem permissão")
    if service.status not in [ServiceStatus.PUBLICADO, ServiceStatus.EM_NEGOCIACAO]:
        raise HTTPException(status_code=400, detail="Status não permite edição")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(service, k, v)
    db.commit()
    db.refresh(service)
    return service


@app.post("/services/{service_id}/offers", response_model=OfferOut)
def create_offer(service_id: int, payload: OfferIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    require_driver(user)
    service = db.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    if service.status in [ServiceStatus.ACEITO, ServiceStatus.CANCELADO, ServiceStatus.ENTREGUE]:
        raise HTTPException(status_code=400, detail="Serviço indisponível para oferta")
    offer = Offer(service_id=service_id, driver_user_id=user.id, **payload.model_dump())
    db.add(offer)
    if service.status == ServiceStatus.PUBLICADO:
        service.status = ServiceStatus.EM_NEGOCIACAO
    db.commit()
    db.refresh(offer)
    if payload.kind == OfferKind.ACCEPT:
        _accept_offer(service, offer, db)
        db.refresh(offer)
    return offer


def _accept_offer(service: Service, offer: Offer, db: Session):
    existing = db.scalar(select(Assignment).where(Assignment.service_id == service.id))
    if existing:
        raise HTTPException(status_code=400, detail="Serviço já atribuído")
    for o in service.offers:
        o.status = OfferStatus.REJECTED if o.id != offer.id else OfferStatus.ACCEPTED
    assignment = Assignment(service_id=service.id, driver_user_id=offer.driver_user_id, accepted_offer_id=offer.id)
    service.status = ServiceStatus.ACEITO
    db.add(assignment)
    db.commit()


@app.get("/services/{service_id}/offers", response_model=list[OfferOut])
def list_offers(service_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    service = db.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    offers = list(db.scalars(select(Offer).where(Offer.service_id == service_id)).all())
    participants = {o.driver_user_id for o in offers}
    if user.id != service.created_by_user_id and user.id not in participants:
        raise HTTPException(status_code=403, detail="Sem permissão")
    return offers


@app.post("/offers/{offer_id}/accept", response_model=OfferOut)
def accept_counter_offer(offer_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    offer = db.get(Offer, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Oferta não encontrada")
    service = db.get(Service, offer.service_id)
    if service.created_by_user_id != user.id:
        raise HTTPException(status_code=403, detail="Sem permissão")
    if offer.kind != OfferKind.COUNTER:
        raise HTTPException(status_code=400, detail="Somente contraproposta pode ser aceita aqui")
    _accept_offer(service, offer, db)
    db.refresh(offer)
    return offer


def _driver_assignment(service_id: int, user_id: int, db: Session) -> tuple[Assignment, Service]:
    assignment = db.scalar(
        select(Assignment).where(and_(Assignment.service_id == service_id, Assignment.driver_user_id == user_id))
    )
    if not assignment:
        raise HTTPException(status_code=403, detail="Somente motorista do assignment")
    service = db.get(Service, service_id)
    return assignment, service


@app.post("/assignments/{service_id}/collect")
def collect(service_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    require_driver(user)
    _, service = _driver_assignment(service_id, user.id, db)
    if service.status != ServiceStatus.ACEITO:
        raise HTTPException(status_code=400, detail="Status inválido")
    service.status = ServiceStatus.COLETADO
    db.commit()
    return {"ok": True, "status": service.status}


@app.post("/assignments/{service_id}/deliver")
def deliver(service_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    require_driver(user)
    _, service = _driver_assignment(service_id, user.id, db)
    if service.status != ServiceStatus.COLETADO:
        raise HTTPException(status_code=400, detail="Status inválido")
    service.status = ServiceStatus.ENTREGUE
    db.commit()
    return {"ok": True, "status": service.status}


@app.post("/drivers/intent")
def set_intent(payload: DriverIntentIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    require_driver(user)
    intent = db.get(DriverIntent, user.id)
    if not intent:
        intent = DriverIntent(driver_user_id=user.id, **payload.model_dump())
        db.add(intent)
    else:
        for k, v in payload.model_dump().items():
            setattr(intent, k, v)
    db.commit()
    return {"ok": True}


@app.get("/drivers/{driver_id}/backhaul_suggestions", response_model=list[BackhaulOut])
def backhaul(
    driver_id: int,
    from_lat: float,
    from_lng: float,
    intended_dest_lat: float,
    intended_dest_lng: float,
    radius_km: float = Query(200, le=1000),
    db: Session = Depends(get_db),
):
    candidates = list(db.scalars(select(Service).where(Service.status == ServiceStatus.PUBLICADO)).all())
    results = []
    for s in candidates:
        pickup_distance = haversine_km(from_lat, from_lng, s.origin_lat, s.origin_lng)
        if pickup_distance > radius_km:
            continue
        trip = haversine_km(s.origin_lat, s.origin_lng, s.dest_lat, s.dest_lng)
        detour = pickup_distance + trip - haversine_km(from_lat, from_lng, s.dest_lat, s.dest_lng)
        price_per_km = float(s.offered_price) / max(trip, 1)
        score = -(pickup_distance * 1.2) - (detour * 2.0) + (price_per_km * 1.0)
        dest_gap = haversine_km(s.dest_lat, s.dest_lng, intended_dest_lat, intended_dest_lng)
        score -= dest_gap * 0.5
        results.append(
            BackhaulOut(
                service_id=s.id,
                title=s.title,
                offered_price=float(s.offered_price),
                pickup_distance_km=round(pickup_distance, 2),
                detour_distance_km=round(detour, 2),
                origin_to_dest_km=round(trip, 2),
                score=round(score, 2),
            )
        )
    return sorted(results, key=lambda x: x.score, reverse=True)[:10]


@app.get("/shipper/my-services", response_model=list[ServiceOut])
def my_services(user: User = Depends(current_user), db: Session = Depends(get_db)):
    require_shipper(user)
    return list(db.scalars(select(Service).where(Service.created_by_user_id == user.id)).all())


@app.get("/driver/my-assignment", response_model=ServiceOut | None)
def my_assignment(user: User = Depends(current_user), db: Session = Depends(get_db)):
    require_driver(user)
    assignment = db.scalar(select(Assignment).where(Assignment.driver_user_id == user.id).order_by(Assignment.id.desc()))
    if not assignment:
        return None
    return db.get(Service, assignment.service_id)
