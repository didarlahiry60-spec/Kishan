from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict

from app.database import get_db
from app.services.bazar_service import bazar_service

router = APIRouter(prefix="/bazar", tags=["Bazar Intelligence"])

class CommodityPriceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name_bn: str
    name_en: Optional[str] = None
    category: str
    district: str
    market_name: Optional[str] = None
    wholesale_min: float
    wholesale_max: float
    wholesale_avg: float
    retail_min: float
    retail_max: float
    retail_avg: float
    unit: str
    price_date: date
    price_trend: str
    price_change_pct: float
    source: str

@router.get("/daily", response_model=List[CommodityPriceOut])
def get_daily_prices(
    district: Optional[str] = Query(None, description="যেমন: বগুড়া, ঢাকা"),
    category: Optional[str] = Query(None, description="যেমন: সবজি, চাল-ডাল"),
    search: Optional[str] = Query(None, description="পণ্যের নাম অনুসন্ধান"),
    target_date: Optional[date] = Query(None, description="নির্দিষ্ট তারিখ (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    দৈনিক বাজারদরের তালিকা (পাইকারি ও খুচরা রেট এবং ট্রেন্ড)
    """
    return bazar_service.get_prices(
        db=db,
        district=district,
        category=category,
        search=search,
        target_date=target_date
    )

@router.get("/summary")
async def get_market_summary(
    district: str = Query("বগুড়া", description="জেলার নাম"),
    db: Session = Depends(get_db)
):
    """
    বাজারের সামগ্রিক পরিস্থিতি, দর ওঠানামা ও এআই পরামর্শ
    """
    return await bazar_service.get_summary(db=db, district=district)

@router.get("/districts")
def get_available_districts():
    """
    সাপোর্টেড জেলা ও প্রধান মোকামের তালিকা
    """
    return bazar_service.get_districts()

@router.get("/categories")
def get_commodity_categories(db: Session = Depends(get_db)):
    """
    সকল পণ্য ক্যাটাগরি
    """
    return bazar_service.get_categories(db=db)
