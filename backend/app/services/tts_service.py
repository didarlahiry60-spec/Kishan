import os
import hashlib
import logging
from pathlib import Path
from typing import Optional
from gtts import gTTS
from app.config import settings

logger = logging.getLogger(__name__)

class TTSService:
    """
    Bengali Text-to-Speech (TTS) Service.
    Converts Bengali agricultural updates, market prices, and advisories to natural MP3 audio.
    """

    def __init__(self):
        self.audio_dir = settings.AUDIO_CACHE_DIR
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    def generate_bengali_audio(self, text_bn: str) -> Optional[str]:
        """
        বাংলা টেক্সট থেকে MP3 অডিও জেনারেট করে ক্যাশ করা ফাইলটির রিলেটিভ URL রিটার্ন করে
        """
        if not text_bn or not text_bn.strip():
            return None

        # টেক্সটের হ্যাশ দিয়ে ক্যাশ নেম তৈরি
        text_hash = hashlib.md5(text_bn.strip().encode("utf-8")).hexdigest()
        file_name = f"{text_hash}.mp3"
        file_path = self.audio_dir / file_name

        if file_path.exists():
            return f"/static/audio_cache/{file_name}"

        try:
            # gTTS বাংলা স্পিচ জেনারেশন
            tts = gTTS(text=text_bn.strip(), lang="bn", slow=False)
            tts.save(str(file_path))
            logger.info(f"[TTSService] Generated audio for: {text_bn[:30]}... -> {file_name}")
            return f"/static/audio_cache/{file_name}"
        except Exception as e:
            logger.warning(f"[TTSService] gTTS audio generation failed (network or rate limit): {e}")
            return None

    def format_price_speech(self, district: str, commodity_name: str, wholesale_avg: float, retail_avg: float, unit: str = "কেজি") -> str:
        return f"{district} বাজারে {commodity_name} এর পাইকারি দর প্রতি {unit} প্রায় {int(wholesale_avg)} টাকা এবং খুচরা বাজার দর {int(retail_avg)} টাকা।"

    def format_daily_briefing_speech(self, district: str, weather_cond: str, temp_max: float, advisory_text: str) -> str:
        return f"আজ {district} এলাকার আবহাওয়া {weather_cond}, সর্বোচ্চ তাপমাত্রা প্রায় {int(temp_max)} ডিগ্রি সেলসিয়াস। কৃষকের জন্য আজকের বিশেষ পরামর্শ: {advisory_text}"

tts_service = TTSService()
