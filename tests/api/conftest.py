import os
import uuid
import pytest

# Inject mock environments BEFORE any application layer import runs
os.environ["DATABASE_URL"] = "sqlite:///./test_minipay.db"
os.environ["API_KEY"] = "test-key"
os.environ["AUTO_CREATE_TABLES"] = "true"

from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

@pytest.fixture(scope="session", autouse=True)
def init_test_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="session")
def api_key():
    return "test-key"

@pytest.fixture
def unique_ref():
    def _make(prefix="TXN"):
        return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"
    return _make

@pytest.fixture
def make_customer(client, api_key, unique_ref):
    def _make(name="Test Customer"):
        ref = unique_ref("CUST")
        r = client.post(
            "/api/customers",
            json={"customer_ref": ref, "name": name},
            headers={"X-API-Key": api_key}
        )
        return ref, r
    return _make
