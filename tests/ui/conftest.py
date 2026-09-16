import os
import uuid
import pytest
import requests

MINIPAY_URL = os.environ.get("MINIPAY_BASE_URL", "http://localhost:8080")
API_KEY = os.environ.get("MINIPAY_API_KEY", "dev-local-key")

@pytest.fixture(scope="session")
def minipay_url():
    return MINIPAY_URL

@pytest.fixture(scope="session")
def api_key():
    return API_KEY

@pytest.fixture(scope="session", autouse=True)
def check_stack_is_up():
    try:
        r = requests.get(f"{MINIPAY_URL}/health", timeout=5)
        assert r.status_code == 200
    except Exception:
        pytest.exit(
            f"MiniPay not reachable at {MINIPAY_URL}. Run: docker compose up -d",
            returncode=2
        )

@pytest.fixture(scope="session")
def seeded_customer(api_key):
    ref = f"UITEST-{uuid.uuid4().hex[:8].upper()}"
    requests.post(
        f"{MINIPAY_URL}/api/customers",
        json={"customer_ref": ref, "name": "UI Test Customer"},
        headers={"X-API-Key": api_key},
        timeout=5
    )
    return ref

@pytest.fixture
def unique_ref():
    return f"UITXN-{uuid.uuid4().hex[:10].upper()}"
