import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool
from main import app
from db import get_session

#$env:PYTHONPATH="."; pytest Test/Character_TEST.py -v

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



def test_create_character(client: TestClient):
    response = client.post("/Characters/", json={
        "name": "Solaire",
        "level": 10,
        "is_hollow": False,
        "main_stat": "Faith"        
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Solaire"
    assert data["level"] == 10
    assert data["id"] is not None

def test_create_character_defaults(client: TestClient):
    response = client.post("/Characters/", json={"name": "Ashen One"})
    assert response.status_code == 200
    data = response.json()
    assert data["level"] == 1
    assert data["is_hollow"] == False

def test_get_all_characters_empty(client: TestClient):
    response = client.get("/Characters/")
    assert response.status_code == 200
    assert response.json() == []

def test_get_all_characters(client: TestClient):
    client.post("/Characters/", json={"name": "Solaire"})
    client.post("/Characters/", json={"name": "Siegmeyer"})
    response = client.get("/Characters/")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_character_by_id(client: TestClient):
    created = client.post("/Characters/", json={"name": "Patches"}).json()
    response = client.get(f"/Characters/{created['id']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Patches"

def test_get_character_not_found(client: TestClient):
    response = client.get("/Characters/999")
    assert response.status_code == 404

def test_update_character(client: TestClient):
    created = client.post("/Characters/", json={"name": "Gwyndolin"}).json()
    response = client.put(f"/Characters/{created['id']}", json={"level": 50})
    assert response.status_code == 200
    assert response.json()["level"] == 50
    assert response.json()["name"] == "Gwyndolin"  

def test_update_character_not_found(client: TestClient):
    response = client.put("/Characters/999", json={"level": 50})
    assert response.status_code == 404

def test_delete_character(client: TestClient):
    created = client.post("/Characters/", json={"name": "Oscar"}).json()
    response = client.delete(f"/Characters/{created['id']}")
    assert response.status_code == 200

def test_deleted_character_not_in_active_list(client: TestClient):
    created = client.post("/Characters/", json={"name": "Oscar"}).json()
    client.delete(f"/Characters/{created['id']}")
    activos = client.get("/Characters/").json()
    ids = [c["id"] for c in activos]
    assert created["id"] not in ids

def test_delete_character_not_found(client: TestClient):
    response = client.delete("/Characters/999")
    assert response.status_code == 404

def test_delete_already_deleted(client: TestClient):
    created = client.post("/Characters/", json={"name": "Oscar"}).json()
    client.delete(f"/Characters/{created['id']}")
    response = client.delete(f"/Characters/{created['id']}")
    assert response.status_code == 404

def test_get_deleted_characters(client: TestClient):
    created = client.post("/Characters/", json={"name": "Oscar"}).json()
    client.delete(f"/Characters/{created['id']}")
    response = client.get("/Characters/deleted")
    assert response.status_code == 200
    ids = [c["id"] for c in response.json()]
    assert created["id"] in ids


def test_restore_character(client: TestClient):
    created = client.post("/Characters/", json={"name": "Lautrec"}).json()
    client.delete(f"/Characters/{created['id']}")
    response = client.patch(f"/Characters/{created['id']}/restore")
    assert response.status_code == 200
    activos = client.get("/Characters/").json()
    ids = [c["id"] for c in activos]
    assert created["id"] in ids

def test_restore_character_not_found(client: TestClient):
    response = client.patch("/Characters/999/restore")
    assert response.status_code == 404