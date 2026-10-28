import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.database import Base, engine, SessionLocal
from app.models.commodity import CommodityPrice
from app.seed_data import seed_database
from app.scheduler import start_scheduler, stop_scheduler

# Routers
from app.api.v1.router_bazar import router as bazar_router
from app.api.v1.router_weather import router as weather_router
from app.api.v1.router_voice import router as voice_router
from app.api.v1.router_profile import router as profile_router
from app.api.v1.router_admin import router as admin_router
from app.api.v1.router_ai_power import router as ai_power_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # স্টার্টআপ: ডেটাবেস টেবিল তৈরি এবং প্রয়োজনে সিডিং
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        count = db.query(CommodityPrice).count()
        if count == 0:
            print("[Startup] Initializing empty database with reference agricultural data...")
            seed_database(force=False)
    finally:
        db.close()

    # ব্যাকগ্রাউন্ড শিডিউলার চালু
    start_scheduler()
    yield
    # শাটডাউন
    stop_scheduler()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="বাংলাদেশের কৃষকদের জন্য এআই চালিত দৈনিক বাজারদর, আবহাওয়া সতর্কতা, বাংলা ভয়েস ও পরামর্শ প্ল্যাটফর্ম",
    lifespan=lifespan
)

# CORS উন্মুক্ত করা যাতে মোবাইল অ্যাপ ও যেকোনো ক্লায়েন্ট থেকে কল করা যায়
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# এপিআই রাউটার মাউন্টিং
app.include_router(bazar_router, prefix=settings.API_V1_PREFIX)
app.include_router(weather_router, prefix=settings.API_V1_PREFIX)
app.include_router(voice_router, prefix=settings.API_V1_PREFIX)
app.include_router(profile_router, prefix=settings.API_V1_PREFIX)
app.include_router(admin_router, prefix=settings.API_V1_PREFIX)
app.include_router(ai_power_router, prefix=settings.API_V1_PREFIX)

# অডিও ক্যাশ ডিরেক্টরি নিশ্চিত করা
settings.AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# স্ট্যাটিক ফাইল ও ওয়েব ইউআই পরিবেশন
if settings.STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")

@app.get("/", include_in_schema=False)
def serve_home():
    index_file = settings.STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Welcome to Kishan Agro-Intelligence API. Visit /docs for API documentation."}

@app.get("/style.css", include_in_schema=False)
def serve_css():
    return FileResponse(settings.STATIC_DIR / "style.css")

@app.get("/app.js", include_in_schema=False)
def serve_js():
    return FileResponse(settings.STATIC_DIR / "app.js")

@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.PROJECT_NAME, "version": settings.VERSION}
