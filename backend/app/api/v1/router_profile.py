from typing import Optional, List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict

from app.database import get_db
from app.models.farmer import FarmerProfile

router = APIRouter(prefix="/profile", tags=["Farmer Profile & Preferences"])

class ProfileRequest(BaseModel):
    device_id: str
    name: Optional[str] = "কৃষক বন্ধু"
    phone: Optional[str] = None
    district: str = "বগুড়া"
    upazila: str = "শিবগঞ্জ"
    favorite_crops: str = "ধান,আলু,পেঁয়াজ"
    sms_alerts_enabled: bool = True
    push_token: Optional[str] = None

class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: str
    name: str
    phone: Optional[str] = None
    district: str
    upazila: str
    favorite_crops: str
    sms_alerts_enabled: bool

@router.get("/{device_id}", response_model=ProfileResponse)
def get_farmer_profile(device_id: str, db: Session = Depends(get_db)):
    """
    ডিভাইস আইডি দিয়ে কৃষকের প্রোফাইল ও পছন্দের ফসল লোড করা
    """
    profile = db.query(FarmerProfile).filter(FarmerProfile.device_id == device_id).first()
    if not profile:
        # স্বয়ংক্রিয় গেস্ট প্রোফাইল ইনিশিয়ালাইজেশন
        profile = FarmerProfile(
            device_id=device_id,
            name="কৃষক বন্ধু",
            district="বগুড়া",
            upazila="সদর",
            favorite_crops="ধান,আলু,পেঁয়াজ"
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.post("", response_model=ProfileResponse)
def save_or_update_profile(req: ProfileRequest, db: Session = Depends(get_db)):
    """
    গেস্ট মোডে সহজে কৃষকের জেলা, উপজেলা ও পছন্দের ফসল সংরক্ষণ (পাসওয়ার্ডহীন)
    """
    profile = db.query(FarmerProfile).filter(FarmerProfile.device_id == req.device_id).first()
    if not profile:
        profile = FarmerProfile(
            device_id=req.device_id,
            name=req.name or "কৃষক বন্ধু",
            phone=req.phone,
            district=req.district,
            upazila=req.upazila,
            favorite_crops=req.favorite_crops,
            sms_alerts_enabled=req.sms_alerts_enabled,
            push_token=req.push_token
        )
        db.add(profile)
    else:
        if req.name:
            profile.name = req.name
        if req.phone is not None:
            profile.phone = req.phone
        profile.district = req.district
        profile.upazila = req.upazila
        profile.favorite_crops = req.favorite_crops
        profile.sms_alerts_enabled = req.sms_alerts_enabled
        if req.push_token:
            profile.push_token = req.push_token
        profile.last_active = datetime.now(timezone.utc)

    db.commit()
    db.refresh(profile)
    return profile
