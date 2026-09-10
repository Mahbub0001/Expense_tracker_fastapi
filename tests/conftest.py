import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# In-memory SQLite database isolated for tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Create fresh database tables for each test and drop them afterwards."""
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Test client with overridden get_db dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_headers(client):
    """Registers a test user, logs in, and returns authorization headers."""
    user_payload = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "password123",
    }
    client.post("/auth/register", json=user_payload)
    login_resp = client.post("/auth/login", json={
        "username": "testuser",
        "password": "password123",
    })
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def second_user_auth_headers(client):
    """Registers a second test user and returns authorization headers for isolation tests."""
    user_payload = {
        "username": "otheruser",
        "email": "otheruser@example.com",
        "password": "otherpassword",
    }
    client.post("/auth/register", json=user_payload)
    login_resp = client.post("/auth/login", json={
        "username": "otheruser",
        "password": "otherpassword",
    })
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
