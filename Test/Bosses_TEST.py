import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool
from main import app
from db import get_session


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_create_boss(client: TestClient):
    response = client.post("/Bosses/", json={
        "name": "Margit",
        "health": 5000,
        "is_optional": False,
        "phase_count": 2
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Margit"
    assert data["health"] == 5000
    assert data["phase_count"] == 2
    assert data["id"] is not None

def test_create_boss_defaults(client: TestClient):
    response = client.post("/Bosses/", json={
        "name": "Radahn",
        "health": 9000
    })
    assert response.status_code == 200
    data = response.json()
    assert data["is_optional"] == False
    assert data["phase_count"] == 1

def test_create_boss_missing_required_fields(client: TestClient):
    response = client.post("/Bosses/", json={"name": "Maliketh"})  
    assert response.status_code == 422


def test_get_all_bosses_empty(client: TestClient):
    response = client.get("/Bosses/")
    assert response.status_code == 200
    assert response.json() == []

def test_get_all_bosses(client: TestClient):
    client.post("/Bosses/", json={"name": "Godrick", "health": 4000})
    client.post("/Bosses/", json={"name": "Rennala", "health": 3500})
    response = client.get("/Bosses/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_boss_by_id(client: TestClient):
    created = client.post("/Bosses/", json={"name": "Placidusax", "health": 12000}).json()
    response = client.get(f"/Bosses/{created['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Placidusax"

def test_get_boss_not_found(client: TestClient):
    response = client.get("/Bosses/999")
    assert response.status_code == 404


def test_update_boss(client: TestClient):
    created = client.post("/Bosses/", json={"name": "Mohg", "health": 8000}).json()
    response = client.put(f"/Bosses/{created['id']}", json={"health": 9500, "phase_count": 2})
    assert response.status_code == 200
    data = response.json()
    assert data["health"] == 9500
    assert data["phase_count"] == 2
    assert data["name"] == "Mohg"  

def test_update_boss_partial(client: TestClient):
    created = client.post("/Bosses/", json={"name": "Morgott", "health": 7000}).json()
    response = client.put(f"/Bosses/{created['id']}", json={"is_optional": True})
    assert response.status_code == 200
    assert response.json()["is_optional"] == True
    assert response.json()["health"] == 7000 

def test_update_boss_not_found(client: TestClient):
    response = client.put("/Bosses/999", json={"health": 100})
    assert response.status_code == 404


def test_delete_boss(client: TestClient):
    created = client.post("/Bosses/", json={"name": "Fire Giant", "health": 6000}).json()
    response = client.delete(f"/Bosses/{created['id']}")
    assert response.status_code == 200

def test_deleted_boss_not_in_active_list(client: TestClient):
    created = client.post("/Bosses/", json={"name": "Godfrey", "health": 10000}).json()
    client.delete(f"/Bosses/{created['id']}")
    activos = client.get("/Bosses/").json()
    ids = [b["id"] for b in activos]
    assert created["id"] not in ids

def test_delete_boss_not_found(client: TestClient):
    response = client.delete("/Bosses/999")
    assert response.status_code == 404

def test_delete_already_deleted_boss(client: TestClient):
    created = client.post("/Bosses/", json={"name": "Elden Beast", "health": 15000}).json()
    client.delete(f"/Bosses/{created['id']}")
    response = client.delete(f"/Bosses/{created['id']}")
    assert response.status_code == 404


def test_get_deleted_bosses(client: TestClient):
    created = client.post("/Bosses/", json={"name": "Lichdragon", "health": 11000}).json()
    client.delete(f"/Bosses/{created['id']}")
    response = client.get("/Bosses/deleted")
    assert response.status_code == 200
    ids = [b["id"] for b in response.json()]
    assert created["id"] in ids

def test_deleted_list_excludes_active(client: TestClient):
    activo = client.post("/Bosses/", json={"name": "Astel", "health": 7000}).json()
    eliminado = client.post("/Bosses/", json={"name": "Ancestor Spirit", "health": 3000}).json()
    client.delete(f"/Bosses/{eliminado['id']}")
    deleted_ids = [b["id"] for b in client.get("/Bosses/deleted").json()]
    assert eliminado["id"] in deleted_ids
    assert activo["id"] not in deleted_ids


def test_restore_boss(client: TestClient):
    created = client.post("/Bosses/", json={"name": "Dragonlord", "health": 13000}).json()
    client.delete(f"/Bosses/{created['id']}")
    response = client.patch(f"/Bosses/{created['id']}/restore")
    assert response.status_code == 200
    activos = client.get("/Bosses/").json()
    ids = [b["id"] for b in activos]
    assert created["id"] in ids

def test_restore_boss_not_found(client: TestClient):
    response = client.patch("/Bosses/999/restore")
    assert response.status_code == 404