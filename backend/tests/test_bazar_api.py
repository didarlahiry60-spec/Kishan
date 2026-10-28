import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"

def test_get_districts():
    res = client.get("/api/v1/bazar/districts")
    assert res.status_code == 200
    districts = res.json()
    assert len(districts) > 0
    names = [d["name_bn"] for d in districts]
    assert "বগুড়া" in names
    assert "ঢাকা" in names

def test_get_categories():
    res = client.get("/api/v1/bazar/categories")
    assert res.status_code == 200
    cats = res.json()
    assert "সব" in cats
    assert "সবজি" in cats

def test_get_daily_prices():
    res = client.get("/api/v1/bazar/daily?district=বগুড়া")
    assert res.status_code == 200
    items = res.json()
    assert len(items) > 0
    first = items[0]
    assert "name_bn" in first
    assert "wholesale_avg" in first
    assert "retail_avg" in first
    assert first["wholesale_avg"] <= first["retail_avg"] # পাইকারি দর খুচরার চেয়ে কম বা সমান

def test_get_daily_prices_category_filter():
    res = client.get("/api/v1/bazar/daily?district=বগুড়া&category=সবজি")
    assert res.status_code == 200
    items = res.json()
    for item in items:
        assert item["category"] == "সবজি"

def test_get_daily_prices_search():
    res = client.get("/api/v1/bazar/daily?district=বগুড়া&search=আলু")
    assert res.status_code == 200
    items = res.json()
    assert len(items) > 0
    for item in items:
        assert "আলু" in item["name_bn"] or "Potato" in (item["name_en"] or "")

def test_get_market_summary():
    res = client.get("/api/v1/bazar/summary?district=বগুড়া")
    assert res.status_code == 200
    data = res.json()
    assert data["district"] == "বগুড়া"
    assert "ai_summary" in data
    assert "bargaining_tip" in data
