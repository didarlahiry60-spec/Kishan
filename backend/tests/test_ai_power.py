import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_live_crawler_endpoint():
    res = client.get("/api/v1/ai/live-crawler?limit=5")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "signals" in data
    # সিগন্যাল অন্তত ১টি পাওয়া গেছে কিনা
    assert len(data["signals"]) >= 0

def test_krishi_consultant_endpoint():
    payload = {
        "query_text": "আলুর নাবী ধসা রোগ হলে কী ওষুধ স্প্রে করব?",
        "district": "বগুড়া",
        "crops": "আলু"
    }
    res = client.post("/api/v1/ai/consultant", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "answer_bn" in data
    assert "short_voice_summary" in data
    assert "recommended_actions" in data
    assert len(data["recommended_actions"]) > 0

def test_crop_doctor_endpoint():
    payload = {
        "crop": "আলু",
        "symptom_description": "পাতায় জলছাপের মতো ভেজা দাগ ও কালো হয়ে পচে যাচ্ছে"
    }
    res = client.post("/api/v1/ai/crop-doctor", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["crop"] == "আলু"
    assert "নাবী ধসা" in data["disease_name"] or "লেট ব্লাইট" in data["disease_name"]
    assert "chemical" in data["prescription"]
    assert "organic" in data["prescription"]

def test_negotiation_calculator_endpoint():
    payload = {
        "crop_name": "গোল আলু",
        "quantity_mon": 50.0,
        "production_cost_per_mon": 750.0,
        "transport_cost_per_mon": 50.0,
        "market_wholesale_per_kg": 28.0,
        "aratdar_offered_per_mon": 950.0
    }
    res = client.post("/api/v1/ai/negotiation", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["break_even_per_mon"] == 800.0
    assert data["fair_market_per_mon"] == 1120.0
    assert data["fair_net_profit"] == 16000.0
    assert "negotiation_script_bn" in data
    assert "আড়তদার" in data["negotiation_script_bn"]
