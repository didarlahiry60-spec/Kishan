from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.commodity import CommodityPrice
from app.models.farmer import FarmerProfile
from app.models.alert import AlertLog
from app.services.bazar_service import bazar_service
from app.services.sms_service import sms_service

router = APIRouter(prefix="/admin", tags=["Admin & Operations"])

class BroadcastAlertRequest(BaseModel):
    title_bn: str
    message_bn: str
    alert_type: str = "weather_emergency" # weather_emergency, price_alert, advisory
    target_district: Optional[str] = "বগুড়া"
    target_crops: Optional[str] = None
    channel: str = "sms" # sms, push, all

@router.post("/sync-now")
async def trigger_price_sync(db: Session = Depends(get_db)):
    """
    ম্যানুয়ালি অথবা শিডিউলড ব্যাকগ্রাউন্ডে দৈনিক বাজারদর স্ক্র্যাপিং ও এআই সিঙ্ক চালু করা
    """
    count = await bazar_service.sync_daily_prices(db=db)
    return {
        "status": "success",
        "message": f"সফলভাবে {count}টি পণ্যের বাজারদর হালনাগাদ করা হয়েছে।",
        "records_processed": count
    }

@router.post("/send-alert")
async def broadcast_alert(
    req: BroadcastAlertRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    কৃষকদের মোবাইল ফোনে জরুরি আবহাওয়া বা বাজার সতর্কবার্তা প্রেরণ
    """
    query = db.query(FarmerProfile)
    if req.target_district and req.target_district != "সকল":
        query = query.filter(FarmerProfile.district == req.target_district)

    farmers = query.all()
    recipients = [f.phone for f in farmers if f.phone and f.sms_alerts_enabled]

    # AlertLog সেভ করা
    log = AlertLog(
        alert_type=req.alert_type,
        title_bn=req.title_bn,
        message_bn=req.message_bn,
        target_district=req.target_district,
        target_crops=req.target_crops,
        channel=req.channel,
        recipients_count=len(recipients),
        status="sent"
    )
    db.add(log)
    db.commit()

    # ব্যাকগ্রাউন্ডে SMS প্রেরণ
    for phone in recipients:
        background_tasks.add_task(sms_service.send_sms, phone, f"[{req.title_bn}]\n{req.message_bn}")

    return {
        "status": "success",
        "recipients_found": len(recipients),
        "target_district": req.target_district,
        "message": f"{len(recipients)} জন কৃষকের কাছে সতর্কবার্তা সফলভাবে প্রেরণ করা হয়েছে।"
    }

@router.get("/stats")
def get_system_stats(db: Session = Depends(get_db)):
    """
    অ্যাপের সার্বিক ডেটা পরিসংখ্যান
    """
    commodity_count = db.query(CommodityPrice).count()
    farmer_count = db.query(FarmerProfile).count()
    alert_count = db.query(AlertLog).count()
    districts = db.query(CommodityPrice.district).distinct().count()

    return {
        "total_commodities": commodity_count,
        "active_districts": districts,
        "registered_farmers": farmer_count,
        "total_alerts_sent": alert_count,
        "system_status": "operational"
    }
