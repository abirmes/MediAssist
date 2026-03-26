
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

# Base de données de test en mémoire
SQLALCHEMY_TEST_URL = "sqlite:///./test.db"
engine_test = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
Base.metadata.create_all(bind=engine_test)

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    """Nettoie la DB avant chaque test."""
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)
    yield


def test_register_success():
    """Test inscription réussie."""
    r = client.post("/auth/register", json={
        "email": "test@test.com",
        "password": "password123"
    })
    assert r.status_code == 201
    assert r.json()["email"] == "test@test.com"
    assert r.json()["role"] == "patient"


def test_register_duplicate_email():
    """Test inscription avec email déjà utilisé."""
    client.post("/auth/register", json={"email": "test@test.com", "password": "pass123"})
    r = client.post("/auth/register", json={"email": "test@test.com", "password": "pass456"})
    assert r.status_code == 400
    assert "déjà utilisé" in r.json()["detail"]


def test_login_success():
    """Test connexion réussie."""
    client.post("/auth/register", json={"email": "test@test.com", "password": "pass123"})
    r = client.post("/auth/login", json={"email": "test@test.com", "password": "pass123"})
    assert r.status_code == 200
    assert "access_token" in r.json()
    assert r.json()["token_type"] == "bearer"


def test_login_wrong_password():
    """Test connexion avec mauvais mot de passe."""
    client.post("/auth/register", json={"email": "test@test.com", "password": "pass123"})
    r = client.post("/auth/login", json={"email": "test@test.com", "password": "wrong"})
    assert r.status_code == 401


def test_get_me_authenticated():
    """Test récupération profil authentifié."""
    client.post("/auth/register", json={"email": "test@test.com", "password": "pass123"})
    login = client.post("/auth/login", json={"email": "test@test.com", "password": "pass123"})
    token = login.json()["access_token"]
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == "test@test.com"


def test_get_me_unauthenticated():
    """Test accès sans token."""
    r = client.get("/auth/me")
    assert r.status_code == 401


def test_health_endpoint():
    """Test endpoint de santé."""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"