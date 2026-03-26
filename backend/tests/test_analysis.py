
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

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
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)
    yield


@pytest.fixture
def auth_token():
    """Fixture : token JWT valide."""
    client.post("/auth/register", json={"email": "test@test.com", "password": "pass123"})
    r = client.post("/auth/login", json={"email": "test@test.com", "password": "pass123"})
    return r.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


def test_get_symptoms(auth_headers):
    """Test récupération liste des symptômes."""
    r = client.get("/analysis/symptoms", headers=auth_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) > 0


def test_analyze_symptoms_success(auth_headers):
    """Test analyse avec symptômes valides."""
    r = client.post("/analysis/analyze",
        headers=auth_headers,
        json={"symptoms": ["chest pain", "sweating"]}
    )
    assert r.status_code == 200
    data = r.json()
    assert "orientation" in data
    assert data["orientation"] in ["urgences", "medecin", "surveillance"]
    assert "severity_score" in data
    assert 0 <= data["severity_score"] <= 100
    assert "risk_level" in data
    assert "consultation_id" in data


def test_analyze_no_symptoms(auth_headers):
    """Test analyse sans symptômes."""
    r = client.post("/analysis/analyze",
        headers=auth_headers,
        json={"symptoms": []}
    )
    assert r.status_code == 400


def test_analyze_unauthenticated():
    """Test analyse sans authentification."""
    r = client.post("/analysis/analyze",
        json={"symptoms": ["fever"]}
    )
    assert r.status_code == 401


def test_get_history(auth_headers):
    """Test récupération historique consultations."""
    # Créer une consultation
    client.post("/analysis/analyze",
        headers=auth_headers,
        json={"symptoms": ["fever", "cough"]}
    )
    r = client.get("/analysis/history", headers=auth_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) >= 1


def test_dashboard_stats(auth_headers):
    """Test statistiques dashboard."""
    r = client.get("/dashboard/stats", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert "total_consultations" in data
    assert "urgences_count" in data
    assert "medecin_count" in data
    assert "surveillance_count" in data