from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.commodity import CommodityPrice
from app.services.tts_service import tts_service
from app.services.weather_service import weather_service
from app.agents.agro_advisory_agent import agro_advisory_agent

router = APIRouter(prefix="/voice", tags=["Bangla Voice & Audio"])

class SpeakRequest(BaseModel):
    text_bn: str

@router.post("/speak")
def generate_voice(req: SpeakRequest):
    """
    যেকোনো বাংলা টেক্সট থেকে স্পষ্ট বাংলা অডিও (MP3) জেনারেট করা
    """
    audio_url = tts_service.generate_bengali_audio(req.text_bn)
    if not audio_url:
        # ফলব্যাক হিসেবে ওয়েব ক্লায়েন্টে লোকাল ওয়েব স্পিচ সিন্থেসিসের টেক্সট প্রদান
        return {
            "status": "fallback_web_tts",
            "audio_url": None,
            "text_bn": req.text_bn
        }
    return {
        "status": "success",
        "audio_url": audio_url,
        "text_bn": req.text_bn
    }

@router.get("/commodity-audio/{commodity_id}")
def get_commodity_voice_audio(commodity_id: int, db: Session = Depends(get_db)):
    """
    একটি নির্দিষ্ট পণ্যের পাইকারি ও খুচরা রেটের জন্য অডিও তৈরি
    """
    item = db.query(CommodityPrice).filter(CommodityPrice.id == commodity_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Commodity not found")

    speech_text = tts_service.format_price_speech(
        district=item.district,
        commodity_name=item.name_bn,
        wholesale_avg=item.wholesale_avg,
        retail_avg=item.retail_avg,
        unit=item.unit
    )

    audio_url = tts_service.generate_bengali_audio(speech_text)
    return {
        "commodity_id": item.id,
        "name_bn": item.name_bn,
        "speech_text": speech_text,
        "audio_url": audio_url
    }

@router.get("/advisory-audio")
async def get_advisory_voice_audio(
    district: str = Query("বগুড়া"),
    crops: str = Query("ধান,আলু")
):
    """
    আজকের আবহাওয়া ও ফসলের পরামর্শের সম্পূর্ণ ভয়েস ব্রিফিং
    """
    crops_list = [c.strip() for c in crops.split(",") if c.strip()]
    weather_data = await weather_service.get_district_forecast(district)
    advisory = await agro_advisory_agent.generate_advisory(district, crops_list, weather_data)

    speech_text = advisory.get("voice_script_bn") or advisory.get("headline_bn") or "আজকের কৃষি আবহাওয়া স্বাভাবিক রয়েছে।"
    audio_url = tts_service.generate_bengali_audio(speech_text)

    return {
        "district": district,
        "speech_text": speech_text,
        "audio_url": audio_url
    }
