import requests
import pytest
from playwright.sync_api import Page, expect

def open_app(page: Page, minipay_url: str):
    page.goto(f"{minipay_url}/", wait_until="domcontentloaded")

# ── 1. App loads and shows healthy ──────────────────────────────────────────
def test_app_loads_and_health_badge_is_green(page: Page, minipay_url: str):
    open_app(page, minipay_url)
    badge = page.get_by_test_id("health-badge")
    expect(badge).to_contain_text("Healthy", timeout=8000)

# ── 2. Search finds an existing transaction ──────────────────────────────────
def test_search_existing_transaction(page: Page, minipay_url: str,
                                     seeded_customer: str, api_key: str,
                                     unique_ref: str):
    requests.post(f"{minipay_url}/api/payments",
        json={"customer_ref": seeded_customer,
              "amount": "750.00",
              "transaction_ref": unique_ref},
        headers={"X-API-Key": api_key}, timeout=5)

    open_app(page, minipay_url)
    page.get_by_test_id("search-input").fill(unique_ref)
    page.get_by_test_id("search-button").click()

    expect(page.get_by_test_id("search-result")).to_be_visible(timeout=8000)
    expect(page.get_by_test_id("search-result")).to_contain_text(unique_ref)
    expect(page.get_by_test_id("search-error")).to_be_hidden()

# ── 3 + 4. Create a payment and validate success ─────────────────────────────
def test_create_payment_success(page: Page, minipay_url: str,
                                seeded_customer: str, api_key: str,
                                unique_ref: str):
    open_app(page, minipay_url)
    page.get_by_test_id("pay-customer").fill(seeded_customer)
    page.get_by_test_id("pay-amount").fill("1500.00")
    page.get_by_test_id("pay-ref").fill(unique_ref)
    page.get_by_test_id("pay-key").fill(api_key)
    page.get_by_test_id("pay-button").click()

    expect(page.get_by_test_id("pay-result")).to_be_visible(timeout=8000)
    expect(page.get_by_test_id("pay-result")).to_contain_text("SUCCESS")
    expect(page.get_by_test_id("pay-error")).to_be_hidden()

    r = requests.get(f"{minipay_url}/api/transactions",
                     params={"ref": unique_ref}, timeout=5)
    assert r.json()["count"] == 1

# ── 5a. Negative: unknown reference shows error ───────────────────────────────
def test_search_unknown_reference_shows_error(page: Page, minipay_url: str):
    open_app(page, minipay_url)
    page.get_by_test_id("search-input").fill("TXN-DOES-NOT-EXIST-99999")
    page.get_by_test_id("search-button").click()

    expect(page.get_by_test_id("search-error")).to_be_visible(timeout=8000)
    expect(page.get_by_test_id("search-result")).to_be_hidden()

# ── 5b. Negative: wrong API key returns 401 ───────────────────────────────────
def test_create_payment_wrong_api_key_shows_error(page: Page, minipay_url: str,
                                                   seeded_customer: str,
                                                   unique_ref: str):
    open_app(page, minipay_url)
    page.get_by_test_id("pay-customer").fill(seeded_customer)
    page.get_by_test_id("pay-amount").fill("100.00")
    page.get_by_test_id("pay-ref").fill(unique_ref)
    page.get_by_test_id("pay-key").fill("wrong-key-entirely")
    page.get_by_test_id("pay-button").click()

    expect(page.get_by_test_id("pay-error")).to_be_visible(timeout=8000)
    expect(page.get_by_test_id("pay-result")).to_be_hidden()

# ── 5c. Negative: unknown customer returns 404 ────────────────────────────────
def test_create_payment_unknown_customer_shows_error(page: Page, minipay_url: str,
                                                      api_key: str,
                                                      unique_ref: str):
    open_app(page, minipay_url)
    page.get_by_test_id("pay-customer").fill("CUST-DOES-NOT-EXIST")
    page.get_by_test_id("pay-amount").fill("100.00")
    page.get_by_test_id("pay-ref").fill(unique_ref)
    page.get_by_test_id("pay-key").fill(api_key)
    page.get_by_test_id("pay-button").click()

    expect(page.get_by_test_id("pay-error")).to_be_visible(timeout=8000)
    expect(page.get_by_test_id("pay-result")).to_be_hidden()
