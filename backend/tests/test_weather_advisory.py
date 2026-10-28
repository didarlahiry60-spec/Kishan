import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_weather_forecast():
    res = client.get("/api/v1/weather/forecast?district=বগুড়া")
    assert res.status_code == 200
    data = res.json()
    assert data["district"] == "বগুড়া"
    assert "current" in data
    assert "temperature" in data["current"]
    assert "daily_forecast" in data
    assert len(data["daily_forecast"]) > 0

def test_get_agro_advisory():
    payload = {
        "district": "বগুড়া",
        "crops": ["ধান", "আলু", "পেঁয়াজ"]
    }
    res = client.post("/api/v1/weather/advisory", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["district"] == "বগুড়া"
    assert "advisory" in data
    adv = data["advisory"]
    assert "headline_bn" in adv
    assert "dos_bn" in adv
    assert len(adv["dos_bn"]) > 0
    assert "donts_bn" in adv
    assert len(adv["donts_bn"]) > 0
    assert "irrigation_advice_bn" in adv
