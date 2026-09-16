def test_create_customer_success(make_customer):
    ref, r = make_customer()
    assert r.status_code == 201
    assert r.json()["customer_ref"] == ref

def test_create_customer_requires_api_key(client, unique_ref):
    r = client.post("/api/customers",
        json={"customer_ref": unique_ref("CUST"), "name": "No Key"})
    assert r.status_code == 401

def test_create_customer_duplicate_returns_409(client, api_key, make_customer):
    ref, _ = make_customer()
    r = client.post("/api/customers",
        json={"customer_ref": ref, "name": "Duplicate"},
        headers={"X-API-Key": api_key})
    assert r.status_code == 409

def test_create_customer_missing_field_returns_422(client, api_key):
    r = client.post("/api/customers",
        json={"name": "No Ref"},
        headers={"X-API-Key": api_key})
    assert r.status_code == 422

def test_get_unknown_customer_returns_404(client):
    r = client.get("/api/customers/99999999/payments")
    assert r.status_code == 404
