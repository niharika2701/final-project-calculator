"""
Integration tests for GET /reports/summary.

Uses FastAPI TestClient with in-memory SQLite — no real server needed.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from main import app

TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(scope="module")
def db_engine():
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def api_client(db_engine):
    TestingSession = sessionmaker(bind=db_engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def auth_headers(api_client):
    """Register and login a test user, return auth headers."""
    api_client.post("/auth/register", json={
        "username": "report_tester",
        "email": "reports@test.com",
        "password": "TestPass123",
    })
    resp = api_client.post("/auth/login", json={
        "username": "report_tester",
        "password": "TestPass123",
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_report_requires_auth(api_client):
    """No token should return 401."""
    resp = api_client.get("/reports/summary")
    assert resp.status_code == 401


def test_empty_report_for_new_user(api_client, auth_headers):
    """Brand new user should get all zeros."""
    resp = api_client.get("/reports/summary", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_calculations"] == 0
    assert data["by_operation"] == {}
    assert data["most_recent"] == []
    assert data["average_a"] == 0.0
    assert data["average_b"] == 0.0
    assert data["average_result"] == 0.0


def test_report_reflects_added_calculations(api_client, auth_headers):
    """After adding calculations totals must update."""
    calcs = [
        {"a": 2, "b": 3, "type": "Add"},
        {"a": 10, "b": 2, "type": "Divide"},
        {"a": 4, "b": 5, "type": "Multiply"},
    ]
    for calc in calcs:
        r = api_client.post("/calculations/", json=calc, headers=auth_headers)
        assert r.status_code == 201

    resp = api_client.get("/reports/summary", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_calculations"] == 3
    assert data["by_operation"]["Add"] == 1
    assert data["by_operation"]["Divide"] == 1
    assert data["by_operation"]["Multiply"] == 1
    assert len(data["most_recent"]) == 3


def test_report_averages(api_client, auth_headers):
    """Averages must be correct across all calculations."""
    resp = api_client.get("/reports/summary", headers=auth_headers)
    data = resp.json()
    # a values: 2, 10, 4 → avg = 16/3 ≈ 5.3333
    assert abs(data["average_a"] - 5.3333) < 0.001


def test_most_recent_capped_at_five(api_client, auth_headers):
    """most_recent must never exceed 5 items."""
    for i in range(3):
        api_client.post("/calculations/", json={"a": i, "b": 1, "type": "Add"}, headers=auth_headers)

    resp = api_client.get("/reports/summary", headers=auth_headers)
    data = resp.json()
    assert data["total_calculations"] == 6
    assert len(data["most_recent"]) == 5


def test_report_scoped_to_user(api_client):
    """A different user must only see their own data."""
    api_client.post("/auth/register", json={
        "username": "other_user",
        "email": "other@test.com",
        "password": "Pass456!",
    })
    resp = api_client.post("/auth/login", json={
        "username": "other_user",
        "password": "Pass456!",
    })
    other_headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

    report = api_client.get("/reports/summary", headers=other_headers)
    assert report.status_code == 200
    assert report.json()["total_calculations"] == 0


def test_report_response_has_correct_schema(api_client, auth_headers):
    """All expected keys must be present in the response."""
    resp = api_client.get("/reports/summary", headers=auth_headers)
    data = resp.json()
    for key in ("total_calculations", "by_operation", "average_a",
                "average_b", "average_result", "most_recent"):
        assert key in data