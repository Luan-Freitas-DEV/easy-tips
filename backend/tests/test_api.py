from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.db import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def reg_and_login(name, email, role):
    r = client.post(
        "/auth/register",
        json={"name": name, "email": email, "password": "123456", "role": role},
    )
    assert r.status_code == 200
    tok = client.post("/auth/login", json={"email": email, "password": "123456"}).json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}


def test_service_offer_and_backhaul_flow():
    shipper = reg_and_login("ship", "ship@x.com", "SHIPPER")
    driver = reg_and_login("drv", "drv@x.com", "DRIVER")
    now = datetime.utcnow()

    service_payload = {
        "title": "Carga SP-Campinas",
        "description": "Paletes",
        "service_type": "LOTACAO",
        "origin_address": "São Paulo",
        "origin_lat": -23.55,
        "origin_lng": -46.63,
        "dest_address": "Campinas",
        "dest_lat": -22.90,
        "dest_lng": -47.06,
        "pickup_window_start": now.isoformat(),
        "pickup_window_end": (now + timedelta(hours=2)).isoformat(),
        "delivery_window_start": (now + timedelta(hours=3)).isoformat(),
        "delivery_window_end": (now + timedelta(hours=8)).isoformat(),
        "offered_price": 1800,
    }
    svc = client.post("/services", json=service_payload, headers=shipper)
    assert svc.status_code == 200
    sid = svc.json()["id"]

    counter = client.post(
        f"/services/{sid}/offers",
        headers=driver,
        json={"kind": "COUNTER", "price": 2000, "message": "faço por 2k"},
    )
    assert counter.status_code == 200
    offer_id = counter.json()["id"]

    accept = client.post(f"/offers/{offer_id}/accept", headers=shipper)
    assert accept.status_code == 200

    collect = client.post(f"/assignments/{sid}/collect", headers=driver)
    assert collect.status_code == 200
    deliver = client.post(f"/assignments/{sid}/deliver", headers=driver)
    assert deliver.status_code == 200

    intent = client.post(
        "/drivers/intent",
        headers=driver,
        json={
            "current_lat": -22.90,
            "current_lng": -47.06,
            "intended_dest_lat": -23.55,
            "intended_dest_lng": -46.63,
            "intended_dest_address": "São Paulo",
            "available_from": now.isoformat(),
            "available_to": (now + timedelta(days=1)).isoformat(),
        },
    )
    assert intent.status_code == 200

    ret_service = dict(service_payload)
    ret_service.update(
        {
            "title": "Retorno Campinas-SP",
            "origin_address": "Campinas",
            "origin_lat": -22.91,
            "origin_lng": -47.07,
            "dest_address": "São Paulo",
            "dest_lat": -23.54,
            "dest_lng": -46.64,
        }
    )
    new_svc = client.post("/services", json=ret_service, headers=shipper)
    assert new_svc.status_code == 200

    sug = client.get(
        "/drivers/2/backhaul_suggestions",
        params={
            "from_lat": -22.90,
            "from_lng": -47.06,
            "intended_dest_lat": -23.55,
            "intended_dest_lng": -46.63,
            "radius_km": 300,
        },
        headers=driver,
    )
    assert sug.status_code == 200
    assert len(sug.json()) >= 1
