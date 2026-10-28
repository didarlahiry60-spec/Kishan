import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_speak_endpoint():
    payload = {"text_bn": "বগুড়া বাজারে আলুর দাম ৩০ টাকা"}
    res = client.post("/api/v1/voice/speak", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "text_bn" in data
    assert data["text_bn"] == payload["text_bn"]

def test_commodity_voice_endpoint():
    # প্রথমে একটি পণ্য আইডি আনা
    prices = client.get("/api/v1/bazar/daily?district=বগুড়া").json()
    assert len(prices) > 0
    cid = prices[0]["id"]

    res = client.get(f"/api/v1/voice/commodity-audio/{cid}")
    assert res.status_code == 200
    data = res.json()
    assert data["commodity_id"] == cid
    assert "speech_text" in data
    assert "বগুড়া" in data["speech_text"]

def test_farmer_profile_flow():
    test_id = "test-device-999"
    # প্রোফাইল ফেচ (অটো তৈরি হওয়া উচিত)
    res = client.get(f"/api/v1/profile/{test_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["device_id"] == test_id

    # প্রোফাইল আপডেট
    update_payload = {
        "device_id": test_id,
        "name": "আব্দুল মজিদ",
        "phone": "01811223344",
        "district": "রাজশাহী",
        "upazila": "গোদাগাড়ী",
        "favorite_crops": "ধান,আম,টমেটো",
        "sms_alerts_enabled": True
    }
    res_up = client.post("/api/v1/profile", json=update_payload)
    assert res_up.status_code == 200
    up_data = res_up.json()
    assert up_data["name"] == "আব্দুল মজিদ"
    assert up_data["district"] == "রাজশাহী"
    assert up_data["favorite_crops"] == "ধান,আম,টমেটো"

def test_admin_sync_and_stats():
    # স্ট্যাটাস চেক
    res_stats = client.get("/api/v1/admin/stats")
    assert res_stats.status_code == 200
    stats = res_stats.json()
    assert stats["total_commodities"] > 0
    assert stats["active_districts"] > 0

    # অ্যালার্ট ব্রডকাস্ট টেস্ট
    alert_payload = {
        "title_bn": "কালবৈশাখী ঝড় সতর্কতা",
        "message_bn": "আজ সন্ধ্যায় দমকা হাওয়াসহ কালবৈশাখী ঝড়ের সম্ভাবনা রয়েছে।",
        "alert_type": "weather_emergency",
        "target_district": "বগুড়া",
        "channel": "sms"
    }
    res_alert = client.post("/api/v1/admin/send-alert", json=alert_payload)
    assert res_alert.status_code == 200
    assert res_alert.json()["status"] == "success"
