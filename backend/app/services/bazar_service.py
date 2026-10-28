import logging
from datetime import date
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.commodity import CommodityPrice
from app.scrapers.dam_scraper import DAMScraper
from app.agents.bazar_ai_agent import BazarAIAgent
from app.seed_data import DISTRICTS_DATA

logger = logging.getLogger(__name__)

class BazarService:
    def __init__(self):
        self.scraper = DAMScraper()
        self.ai_agent = BazarAIAgent()

    def get_prices(
        self,
        db: Session,
        district: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        target_date: Optional[date] = None
    ) -> List[CommodityPrice]:
        query = db.query(CommodityPrice)

        if district:
            query = query.filter(CommodityPrice.district == district)
        if category and category != "সব":
            query = query.filter(CommodityPrice.category == category)
        if search:
            query = query.filter(
                (CommodityPrice.name_bn.ilike(f"%{search}%")) |
                (CommodityPrice.name_en.ilike(f"%{search}%"))
            )
        if target_date:
            query = query.filter(CommodityPrice.price_date == target_date)
        else:
            # সর্বশেষ তারিখের ডেটা
            latest_date = db.query(func.max(CommodityPrice.price_date)).scalar()
            if latest_date:
                query = query.filter(CommodityPrice.price_date == latest_date)

        return query.order_by(CommodityPrice.category, CommodityPrice.name_bn).all()

    async def get_summary(self, db: Session, district: str) -> Dict[str, Any]:
        """
        বাজারদরের সামগ্রিক বিশ্লেষণ: শীর্ষ বৃদ্ধি, শীর্ষ হ্রাস, প্রধান প্রধান পণ্য এবং এআই মতামত
        """
        latest_date = db.query(func.max(CommodityPrice.price_date)).scalar()
        query = db.query(CommodityPrice).filter(
            CommodityPrice.district == district
        )
        if latest_date:
            query = query.filter(CommodityPrice.price_date == latest_date)

        items = query.all()
        if not items:
            # ফলব্যাক যদি ঐ জেলায় ডেটা না থাকে
            items = db.query(CommodityPrice).filter(CommodityPrice.district == "ঢাকা").all()

        items_dict = [
            {
                "id": it.id,
                "name_bn": it.name_bn,
                "category": it.category,
                "wholesale_avg": it.wholesale_avg,
                "retail_avg": it.retail_avg,
                "unit": it.unit,
                "price_trend": it.price_trend,
                "price_change_pct": it.price_change_pct,
                "market_name": it.market_name
            }
            for it in items
        ]

        top_gainers = sorted([it for it in items_dict if it["price_trend"] == "up"], key=lambda x: x["price_change_pct"], reverse=True)[:3]
        top_losers = sorted([it for it in items_dict if it["price_trend"] == "down"], key=lambda x: x["price_change_pct"])[:3]

        # এআই অ্যানালাইসিস আনা
        ai_insights = await self.ai_agent.analyze_market_trends(district, items_dict)

        return {
            "district": district,
            "date": str(latest_date or date.today()),
            "total_items": len(items_dict),
            "top_gainers": top_gainers,
            "top_losers": top_losers,
            "ai_summary": ai_insights.get("market_summary_bn"),
            "bargaining_tip": ai_insights.get("bargaining_tip_bn"),
            "high_risk_crops": ai_insights.get("high_risk_crops", [])
        }

    def get_districts(self) -> List[Dict[str, Any]]:
        return [
            {"name_bn": dist, "division": info["division"], "market": info["market"]}
            for dist, info in DISTRICTS_DATA.items()
        ]

    def get_categories(self, db: Session) -> List[str]:
        results = db.query(CommodityPrice.category).distinct().all()
        cats = [r[0] for r in results if r[0]]
        return ["সব"] + cats

    async def sync_daily_prices(self, db: Session, target_date: Optional[date] = None) -> int:
        target_date = target_date or date.today()
        logger.info(f"[BazarService] Starting daily market price sync for {target_date}...")
        scraped_data = await self.scraper.fetch_dam_prices(target_date)

        count = 0
        for item in scraped_data:
            existing = db.query(CommodityPrice).filter(
                CommodityPrice.name_bn == item["name_bn"],
                CommodityPrice.district == item.get("district", "ঢাকা"),
                CommodityPrice.price_date == target_date
            ).first()

            if existing:
                existing.wholesale_min = item["wholesale_min"]
                existing.wholesale_max = item["wholesale_max"]
                existing.wholesale_avg = item["wholesale_avg"]
                existing.retail_min = item["retail_min"]
                existing.retail_max = item["retail_max"]
                existing.retail_avg = item["retail_avg"]
                existing.price_trend = item.get("price_trend", "stable")
                existing.price_change_pct = item.get("price_change_pct", 0.0)
            else:
                new_record = CommodityPrice(
                    name_bn=item["name_bn"],
                    name_en=item.get("name_en"),
                    category=item.get("category", "সবজি"),
                    district=item.get("district", "ঢাকা"),
                    market_name=item.get("market_name", "মোকাম"),
                    wholesale_min=item["wholesale_min"],
                    wholesale_max=item["wholesale_max"],
                    wholesale_avg=item["wholesale_avg"],
                    retail_min=item["retail_min"],
                    retail_max=item["retail_max"],
                    retail_avg=item["retail_avg"],
                    unit=item.get("unit", "কেজি"),
                    price_date=target_date,
                    price_trend=item.get("price_trend", "stable"),
                    price_change_pct=item.get("price_change_pct", 0.0),
                    source=item.get("source", "dam")
                )
                db.add(new_record)
            count += 1

        db.commit()
        logger.info(f"[BazarService] Sync completed. Upserted {count} records.")
        return count

bazar_service = BazarService()
