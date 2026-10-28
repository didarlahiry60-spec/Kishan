from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class FarmerProfile(Base):
    __tablename__ = "farmer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, default="কৃষক বন্ধু")
    phone = Column(String, index=True, nullable=True)
    district = Column(String, default="বগুড়া", nullable=False)
    upazila = Column(String, default="সদর", nullable=False)
    favorite_crops = Column(String, default="ধান,আলু,পেঁয়াজ")
    
    sms_alerts_enabled = Column(Boolean, default=True)
    push_token = Column(String, nullable=True)
    
    last_active = Column(DateTime, default=utc_now)
    created_at = Column(DateTime, default=utc_now)
