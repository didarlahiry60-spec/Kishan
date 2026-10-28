import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from app.config import settings
from app.services.tts_service import tts_service

logger = logging.getLogger(__name__)

class KrishiConsultant:
    """
    Conversational AI Krishi Consultant & Voice Assistant.
    Provides expert agricultural diagnostics, market advice, and answers farmer queries in natural spoken Bengali.
    """

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    async def answer_farmer_query(
        self,
        query_text: str,
        district: str = "বগুড়া",
        crops: Optional[str] = "ধান,আলু,পেঁয়াজ"
    ) -> Dict[str, Any]:
        """
        কৃষকের মৌখিক বা টেক্সট প্রশ্নের সরাসরি সমাধান ও বাংলা ভয়েস জেনারেশন
        """
        if self.client:
            prompt = f"""
আপনি বাংলাদেশ কৃষি গবেষণা ইনস্টিটিউট (BARI) এবং ধান গবেষণা ইনস্টিটিউটের (BRRI) একজন অভিজ্ঞ কৃষি বিজ্ঞানী ও সম্প্রসারণ কর্মকর্তা।
কৃষকের এলাকা: {district}
প্রধান ফসল: {crops}
কৃষকের প্রশ্ন: "{query_text}"

অনুগ্রহ করে অত্যন্ত বিনয়ী, আন্তরিক ও খাঁটি কথ্য বাংলায় ৩-৪ লাইনে কৃষকের প্রশ্নের স্পষ্ট সমাধান দিন। 
প্রয়োজনে সঠিক ওষুধের নাম (যেমন মেনকোজেব, কার্বেনডাজিম, ডায়াথেন এম-৪৫ ইত্যাদি) এবং সঠিক মাত্রা (গ্রাম/লিটার) উল্লেখ করুন।

JSON ফরম্যাটে উত্তর দিন:
{{
  "answer_bn": "কৃষকের জন্য লিখিত বিস্তারিত দিকনির্দেশনা (৩-৪ লাইন)",
  "short_voice_summary": "কৃষকের কানে পড়ে শোনানোর মতো মিষ্টি ও স্পষ্ট সংক্ষিপ্ত ২ লাইনের অডিও বার্তা",
  "recommended_actions": ["পয়েন্ট ১", "পয়েন্ট ২"],
  "caution_note": "একটি সতর্কতা (যদি থাকে)"
}}
"""
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a warm, highly knowledgeable Bangladeshi Krishi Officer. Respond only in JSON with Bengali text."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.3
                )
                res_json = json.loads(resp.choices[0].message.content)
                voice_text = res_json.get("short_voice_summary") or res_json.get("answer_bn")
                audio_url = tts_service.generate_bengali_audio(voice_text)
                res_json["audio_url"] = audio_url
                return res_json
            except Exception as e:
                logger.warning(f"[KrishiConsultant] OpenAI call error: {e}. Falling back to agronomic knowledge base.")

        # অফলাইন এক্সপার্ট নলেজ বেস
        return self._rulebase_agri_answer(query_text, district)

    def _rulebase_agri_answer(self, query: str, district: str) -> Dict[str, Any]:
        q = query.lower()

        # ১. আলুর রোগ / ব্লাইট
        if any(w in q for w in ["আলু", "ধসা", "পচা", "ব্লাইট", "দাগ"]):
            ans = "আলুর নাবী ধসা (Late Blight) বা পাতা পোড়া রোগ প্রতিরোধে প্রতি লিটার পানিতে ২ গ্রাম ম্যানকোজেব (যেমন ডায়াথেন এম-৪৫) অথবা রিডোমিল গোল্ড মিশিয়ে বিকেলে গাছে ভালোভাবে স্প্রে করুন। জমিতে অতিরিক্ত পানি থাকলে দ্রুত নালা কেটে বের করে দিন।"
            voice = f"{district} এর কৃষক ভাই, আপনার আলুর জমিতে ২ গ্রাম ম্যানকোজেব প্রতি লিটার পানিতে গুলে স্প্রে করুন এবং ক্ষেতের জমা পানি দ্রুত বের করে দিন।"
            actions = [
                "ম্যানকোজেব বা রিডোমিল গোল্ড ২ গ্রাম/লিটার পানিতে স্প্রে করুন।",
                "আক্রান্ত পাতা ও গাছ তুলে মাটিতে পুঁতে ফেলুন।",
                "আকাশ মেঘলা থাকলে ইউরিয়া সার দেওয়া বন্ধ রাখুন।"
            ]
            caution = "কড়া রোদে বা বৃষ্টির মধ্যে স্প্রে করবেন না।"

        # ২. ধানের পোকা / ব্লাস্ট
        elif any(w in q for w in ["ধান", "ব্লাস্ট", "মাজরা", "ঘাসফড়িং", "হলুদ"]):
            ans = "ধানের ব্লাস্ট রোগ হলে ট্রাইসাইক্লাজল গোত্রের ছত্রাকনাশক (যেমন ট্রুপার বা নেটিভো) প্রতি লিটার পানিতে ০.৭৫ গ্রাম হারে মিশিয়ে স্প্রে করুন। মাজরা পোকা থাকলে কার্বোফুরান বা ডায়াজিনন অনুমোদিত মাত্রায় প্রয়োগ করুন এবং ধানের জমিতে ২-৩ ইঞ্চি পানি ধরে রাখুন।"
            voice = f"ধানের পাতা হলুদ বা ব্লাস্ট দেখা দিলে নেটিভো অথবা ট্রুপার স্প্রে করুন এবং জমিতে পর্যাপ্ত পানি ধরে রাখুন।"
            actions = [
                "ট্রাইসাইক্লাজল বা নেটিভো ছত্রাকনাশক স্প্রে করুন।",
                "মাজরা পোকা দমনে জমিতে ডালপালা পুঁতে পার্চিং (পাখি বসার ব্যবস্থা) করুন।",
                "ইউরিয়া সারের মাত্রা কমিয়ে পটাশ সার প্রয়োগ করুন।"
            ]
            caution = "শিশির ভেজা সকালে স্প্রে করবেন না, রোদ ওঠার পর স্প্রে করুন।"

        # ৩. পেঁয়াজ / মরিচ
        elif any(w in q for w in ["মরিচ", "পেঁয়াজ", "কোকড়ানো", "পাতা কোঁকড়া"]):
            ans = "মরিচ বা পেঁয়াজের পাতা কোঁকড়ানো মূলত থ্রিপস বা সাদা মাছি পোকার কারণে হয়। এটি দমনে ইমিডাক্লোপ্রিড গ্রুপের কীটনাশক (যেমন অ্যাডমায়ার বা টিডো) প্রতি লিটার পানিতে ০.৫ মিলি হারে স্প্রে করুন।"
            voice = "মরিচ বা পেঁয়াজের পাতা কোঁকড়ানো রোধে ইমিডাক্লোপ্রিড কীটনাশক প্রতি লিটার পানিতে আধা মিলি হারে স্প্রে করুন।"
            actions = [
                "অ্যাডমায়ার বা টিডো ০.৫ মিলি/লিটার পানিতে স্প্রে করুন।",
                "জমিতে হলুদ আঠালো ফাঁদ (Yellow Sticky Trap) ব্যবহার করুন।"
            ]
            caution = "কীটনাশক স্প্রে করার অন্তত ৭ দিনের মধ্যে মরিচ বা সবজি তুলবেন না।"

        # ৪. সাধারণ বাজারদর ও বিক্রয় প্রশ্ন
        elif any(w in q for w in ["দাম", "বিক্রি", "লাভ", "আড়ত"]):
            ans = f"{district} মোকামে সরকারি পাইকারি রেট জেনে তবেই ফসল বিক্রি করুন। পাইকারি দরের চেয়ে অতিরিক্ত কমিশন দাবি করলে সরাসরি স্থানীয় কৃষি বিপণন কর্মকর্তার তালিকাভুক্ত আড়তে যান।"
            voice = f"{district} বাজারে আপনার ফসলের পাইকারি রেট জেনে বিক্রি করুন, মধ্যস্বত্বভোগীদের ফাঁদে পা দেবেন না।"
            actions = [
                "অ্যাপের বাজারদর ট্যাবে আজকের সরকারি পাইকারি সর্বনিম্ন ও সর্বোচ্চ রেট দেখে নিন।",
                "কমিশন ও পরিবহন খরচ আগেই পরিষ্কারভাবে নির্ধারণ করুন।"
            ]
            caution = "আড়তদারের ওজনে কারচুপি রোধে ডিজিটাল স্কেল ব্যবহার করুন।"

        else:
            ans = f"কৃষক বন্ধু, আপনার প্রশ্নের জন্য স্থানীয় উপজেলা কৃষি কর্মকর্তার সহায়তা নিতে পারেন। এছাড়াও ফসলের সুষম পুষ্টির জন্য সঠিক সময়ে সার, পরিমিত সেচ এবং আগাছা দমন নিশ্চিত রাখুন।"
            voice = "আপনার ফসলের সঠিক পরিচর্যার জন্য নিয়মিত আগাছা দমন করুন এবং পরিমিত সেচ দিন।"
            actions = ["মাটির আর্দ্রতা বজায় রাখুন।", "উপজেলা কৃষি অফিসে নমুনা নিয়ে যোগাযোগ করুন।"]
            caution = "অননুমোদিত রাসায়নিক ব্যবহার থেকে বিরত থাকুন।"

        audio_url = tts_service.generate_bengali_audio(voice)
        return {
            "answer_bn": ans,
            "short_voice_summary": voice,
            "recommended_actions": actions,
            "caution_note": caution,
            "audio_url": audio_url
        }

krishi_consultant = KrishiConsultant()
