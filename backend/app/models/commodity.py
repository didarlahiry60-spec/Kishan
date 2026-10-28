from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Index
from app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class CommodityPrice(Base):
    __tablename__ = "commodity_prices"

    id = Column(Integer, primary_key=True, index=True)
    name_bn = Column(String, index=True, nullable=False)
    name_en = Column(String, index=True, nullable=True)
    category = Column(String, index=True, nullable=False)  # সবজি, চাল-ডাল, মসলা, তৈলবীজ, ফল
    district = Column(String, index=True, nullable=False)  # ঢাকা, বগুড়া, রাজশাহী ইত্যাদি
    market_name = Column(String, nullable=True)            # মোকাম / হাটের নাম
    
    # পাইকারি দর (Wholesale)
    wholesale_min = Column(Float, nullable=False)
    wholesale_max = Column(Float, nullable=False)
    wholesale_avg = Column(Float, nullable=False)
    
    # খুচরা দর (Retail)
    retail_min = Column(Float, nullable=False)
    retail_max = Column(Float, nullable=False)
    retail_avg = Column(Float, nullable=False)
    
    unit = Column(String, default="কেজি")                  # কেজি, পিস, হালি, লিটার
    price_date = Column(Date, index=True, nullable=False)
    
    price_trend = Column(String, default="stable")         # up, down, stable
    price_change_pct = Column(Float, default=0.0)          # শতকরা পরিবর্তন
    
    source = Column(String, default="dam")                 # dam, ai_agent, verified
    created_at = Column(DateTime, default=utc_now)

    __table_args__ = (
        Index("idx_district_date_cat", "district", "price_date", "category"),
    )
