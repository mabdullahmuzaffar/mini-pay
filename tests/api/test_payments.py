import time

def _pay(client, api_key, customer_ref, txn_ref, amount="1000.00"):
    return client.post("/api/payments",
        json={"customer_ref": customer_ref, "amount": amount, "transaction_ref": txn_ref},
        headers={"X-API-Key": api_key})

def test_create_payment_success(make_customer, client, api_key, unique_ref):
    ref, _ = make_customer()
    r = _pay(client, api_key, ref, unique_ref())
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "SUCCESS"
    assert len(body["callbacks"]) == 1
    assert body["callbacks"][0]["http_status"] == 200

def test_create_payment_requires_api_key(make_customer, client, unique_ref):
    ref, _ = make_customer()
    r = client.post("/api/payments",
        json={"customer_ref": ref, "amount": "100.00", "transaction_ref": unique_ref()})
    assert r.status_code == 401

def test_create_payment_unknown_customer_returns_404(client, api_key, unique_ref):
    r = _pay(client, api_key, "CUST-DOESNT-EXIST", unique_ref())
    assert r.status_code == 404

def test_create_payment_negative_amount_returns_422(make_customer, client, api_key, unique_ref):
    ref, _ = make_customer()
    r = _pay(client, api_key, ref, unique_ref(), amount="-50.00")
    assert r.status_code == 422

def test_payment_is_idempotent(make_customer, client, api_key, unique_ref):
    ref, _ = make_customer()
    txn_ref = unique_ref()
    r1 = _pay(client, api_key, ref, txn_ref)
    r2 = _pay(client, api_key, ref, txn_ref)
    assert r1.status_code == 201
    assert r2.status_code == 200          
    assert r1.json()["id"] == r2.json()["id"]   

def test_get_payment_by_id(make_customer, client, api_key, unique_ref):
    ref, _ = make_customer()
    created = _pay(client, api_key, ref, unique_ref())
    pid = created.json()["id"]
    r = client.get(f"/api/payments/{pid}")
    assert r.status_code == 200
    for field in ("id", "transaction_ref", "amount", "status", "callbacks"):
        assert field in r.json()

def test_get_unknown_payment_returns_404(client):
    r = client.get("/api/payments/99999999")
    assert r.status_code == 404   

def test_search_by_reference(make_customer, client, api_key, unique_ref):
    ref, _ = make_customer()
    txn_ref = unique_ref()
    _pay(client, api_key, ref, txn_ref)
    r = client.get("/api/transactions", params={"ref": txn_ref})
    assert r.status_code == 200
    assert r.json()["count"] == 1
    assert r.json()["results"][0]["transaction_ref"] == txn_ref

def test_search_missing_param_returns_422(client):
    r = client.get("/api/transactions")
    assert r.status_code == 422

def test_health_response_time(client):
    start = time.perf_counter()
    r = client.get("/health")
    elapsed = time.perf_counter() - start
    assert r.status_code == 200
    assert elapsed < 1.0    
