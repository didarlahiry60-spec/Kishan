from typing import Optional, List
from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.agents.live_market_crawler import live_market_crawler
from app.agents.krishi_consultant import krishi_consultant
from app.agents.crop_doctor import crop_doctor
from app.services.negotiation_calculator import negotiation_calculator

router = APIRouter(prefix="/ai", tags=["AI Full-Power Agro Engine"])

class QueryRequest(BaseModel):
    query_text: str
    district: str = "বগুড়া"
    crops: Optional[str] = "ধান,আলু,পেঁয়াজ"

class DiagnoseRequest(BaseModel):
    crop: str = "আলু"
    symptom_description: str = "পাতায় জলছাপের মতো ভেজা দাগ ও কালো হয়ে পচে যাচ্ছে"

class NegotiationRequest(BaseModel):
    crop_name: str = "গোল আলু"
    quantity_mon: float = 50.0
    production_cost_per_mon: float = 750.0
    transport_cost_per_mon: float = 50.0
    market_wholesale_per_kg: float = 28.0
    aratdar_offered_per_mon: float = 950.0

@router.get("/live-crawler")
async def get_live_crawler_signals(limit: int = Query(10, ge=1, le=30)):
    """
    ইন্টারনেট থেকে সরাসরি লাইভ কৃষি বাজার সংবাদ ও স্পট প্রাইস সিগন্যাল
    """
    signals = await live_market_crawler.crawl_live_market_signals(limit=limit)
    return {
        "status": "success",
        "total_signals": len(signals),
        "signals": signals
    }

@router.post("/consultant")
async def ask_krishi_consultant(req: QueryRequest):
    """
    এআই কৃষি পরামর্শক ও ভয়েস স্পিকার (যেকোনো রোগ, পরিচর্যা বা বাজার প্রশ্ন)
    """
    return await krishi_consultant.answer_farmer_query(
        query_text=req.query_text,
        district=req.district,
        crops=req.crops
    )

@router.post("/crop-doctor")
def diagnose_crop_disease(req: DiagnoseRequest):
    """
    এআই ক্রপ ডক্টর: লক্ষণ দেখে রোগ নির্ণয় ও তাৎক্ষণিক প্রেসক্রিপশন
    """
    return crop_doctor.diagnose_crop_issue(
        crop=req.crop,
        symptom_keyword=req.symptom_description
    )

@router.get("/crop-diseases")
def list_known_diseases():
    """
    প্রধান ফসলের স্যাম্পল রোগের তালিকা
    """
    return crop_doctor.get_sample_diseases()

@router.post("/negotiation")
def calculate_negotiation(req: NegotiationRequest):
    """
    আড়তদার নেগোসিয়েশন ও লাভ-ক্ষতি ক্যালকুলেটর (কথোপকথনের স্ক্রিপ্ট সহ)
    """
    return negotiation_calculator.calculate_deal(
        crop_name=req.crop_name,
        quantity_mon=req.quantity_mon,
        production_cost_per_mon=req.production_cost_per_mon,
        transport_cost_per_mon=req.transport_cost_per_mon,
        market_wholesale_per_kg=req.market_wholesale_per_kg,
        aratdar_offered_per_mon=req.aratdar_offered_per_mon
    )
