from typing import List, Optional
from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.weather_service import weather_service
from app.agents.agro_advisory_agent import agro_advisory_agent

router = APIRouter(prefix="/weather", tags=["Weather & Agro-Advisory"])

class AdvisoryRequest(BaseModel):
    district: str = "বগুড়া"
    crops: List[str] = ["ধান", "আলু", "পেঁয়াজ"]

@router.get("/forecast")
async def get_weather_forecast(
    district: str = Query("বগুড়া", description="জেলার নাম")
):
    """
    নির্দিষ্ট জেলার হাইপার-লোকাল ৭ দিনের আবহাওয়া পূর্বাভাস
    """
    return await weather_service.get_district_forecast(district)

@router.post("/advisory")
async def get_agro_advisory(
    req: AdvisoryRequest
):
    """
    আবহাওয়া ও কৃষকের নির্বাচিত ফসলের ভিত্তিতে এআই এগ্রো-এডভাইজরি (করণীয়, বর্জনীয়, সেচ)
    """
    weather_data = await weather_service.get_district_forecast(req.district)
    advisory = await agro_advisory_agent.generate_advisory(
        district=req.district,
        crops=req.crops,
        weather_data=weather_data
    )
    return {
        "district": req.district,
        "crops": req.crops,
        "weather_summary": weather_data.get("current", {}),
        "advisory": advisory
    }
