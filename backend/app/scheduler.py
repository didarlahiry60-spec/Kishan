import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.config import settings
from app.database import SessionLocal
from app.services.bazar_service import bazar_service

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def scheduled_daily_sync():
    logger.info("[Scheduler] Executing scheduled 06:00 AM daily market price and advisory sync...")
    db = SessionLocal()
    try:
        count = await bazar_service.sync_daily_prices(db)
        logger.info(f"[Scheduler] Daily sync finished successfully. {count} records updated.")
    except Exception as e:
        logger.error(f"[Scheduler] Daily sync job failed: {e}")
    finally:
        db.close()

def start_scheduler():
    if not scheduler.running:
        trigger = CronTrigger(
            hour=settings.DAILY_SYNC_HOUR,
            minute=settings.DAILY_SYNC_MINUTE,
            timezone="Asia/Dhaka"
        )
        scheduler.add_job(
            scheduled_daily_sync,
            trigger=trigger,
            id="daily_bazar_sync",
            replace_existing=True
        )
        scheduler.start()
        logger.info(f"[Scheduler] Background scheduler started. Daily sync set for {settings.DAILY_SYNC_HOUR:02d}:{settings.DAILY_SYNC_MINUTE:02d} BST.")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("[Scheduler] Background scheduler stopped.")
