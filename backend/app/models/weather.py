from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Text, Index
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class WeatherRecord(Base):
    __tablename__ = "weather_records"

    id = Column(Integer, primary_key=True, index=True)
    district = Column(String, index=True, nullable=False)
    date = Column(Date, index=True, nullable=False)
    
    # আবহাওয়া মেট্রিক্স
    temp_max = Column(Float, nullable=False)
    temp_min = Column(Float, nullable=False)
    precipitation_sum = Column(Float, default=0.0)      # মিলিমিটার (mm)
    precipitation_prob = Column(Integer, default=0)      # %
    humidity = Column(Integer, default=70)               # %
    wind_speed = Column(Float, default=10.0)             # কিমি/ঘণ্টা
    
    weather_condition = Column(String, default="পরিষ্কার") # বৃষ্টি, মেঘলা, রৌদ্রোজ্জ্বল ইত্যাদি
    risk_level = Column(String, default="low")           # low, moderate, high, severe
    
    # এআই এগ্রো-এডভাইজরি
    advisory_headline_bn = Column(String, nullable=True)
    advisory_dos_bn = Column(Text, nullable=True)        # করণীয় (JSON বা লাইন ব্রেক)
    advisory_donts_bn = Column(Text, nullable=True)      # বর্জনীয়
    irrigation_advice_bn = Column(Text, nullable=True)   # সেচ ও পরিচর্যা
    target_crops = Column(String, nullable=True)         # যেসব ফসলের জন্য প্রযোজ্য
    
    source = Column(String, default="open_meteo")
    created_at = Column(DateTime, default=utc_now)

    __table_args__ = (
        Index("idx_district_date_weather", "district", "date"),
    )
