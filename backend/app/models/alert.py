from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class AlertLog(Base):
    __tablename__ = "alert_logs"

    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String, nullable=False) # weather_emergency, price_alert, advisory
    title_bn = Column(String, nullable=False)
    message_bn = Column(Text, nullable=False)
    target_district = Column(String, nullable=True)
    target_crops = Column(String, nullable=True)
    channel = Column(String, default="in_app")  # in_app, push, sms
    recipients_count = Column(Integer, default=0)
    status = Column(String, default="sent")     # sent, failed
    created_at = Column(DateTime, default=utc_now)
