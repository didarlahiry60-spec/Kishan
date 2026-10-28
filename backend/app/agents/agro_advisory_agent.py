import json
import logging
from typing import Dict, Any, List
from openai import OpenAI
from app.config import settings

logger = logging.getLogger(__name__)

class AgroAdvisoryAgent:
    """
    OpenAI-powered Agro-Advisory Agent.
    Generates actionable Bengali dos/don'ts, irrigation guidelines, and crop-specific care
    based on weather forecast metrics (BRRI / BARI agronomic best practices).
    """

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    async def generate_advisory(self, district: str, crops: List[str], weather_data: Dict[str, Any]) -> Dict[str, Any]:
        crops_str = ", ".join(crops) if crops else "ধান, আলু, পেঁয়াজ"
        
        current = weather_data.get("current", {})
        daily = weather_data.get("daily_forecast", [{}])[0]
        
        rain_sum = daily.get("precipitation_sum", 0.0)
        rain_prob = daily.get("precipitation_prob", 0)
        temp_max = daily.get("temp_max", 30.0)
        wind = daily.get("wind_speed", 10.0)
        cond = daily.get("condition_bn", "স্বাভাবিক")

        if self.client:
            prompt = f"""
আপনি একজন অভিজ্ঞ বাংলাদেশি কৃষি কর্মকর্তা ও এগ্রোনোমিস্ট (BRRI/BARI বিশেষজ্ঞ)।
কৃষকের জেলা: {district}
কৃষকের প্রধান ফসলসমূহ: {crops_str}

আসন্ন আবহাওয়া পূর্বাভাস:
- আকাশ/অবস্থা: {cond}
- তাপমাত্রা: সর্বোচ্চ {temp_max}°C
- বৃষ্টির সম্ভাবনা: {rain_prob}%
- সম্ভাব্য বৃষ্টিপাতের পরিমাণ: {rain_sum} মিমি
- বাতাসের গতি: {wind} কিমি/ঘণ্টা

দয়া করে কৃষকের ফসল রক্ষার জন্য স্পষ্ট, সহজ খাঁটি বাংলায় ব্যবহারিক দিকনির্দেশনা দিন।
JSON রেসপন্স দিন এই ফরমেটে:
{{
  "headline_bn": "১ লাইনের মূল সতর্কতা বা বার্তা",
  "risk_level": "low" | "moderate" | "high" | "severe",
  "dos_bn": [
    "করণীয় ১ (ফসল নির্দিষ্ট)",
    "করণীয় ২",
    "করণীয় ৩"
  ],
  "donts_bn": [
    "বর্জনীয় ১ (যেমন স্প্রে বা সারের নিষেধাজ্ঞা)",
    "বর্জনীয় ২"
  ],
  "irrigation_advice_bn": "সেচ দেওয়া যাবে কি যাবে না এবং মাটি আর্দ্রতার পরামর্শ (১-২ লাইন)",
  "voice_script_bn": "কৃষকের স্পিকারে পড়ে শোনানোর জন্য সংক্ষেপিত ২-৩ লাইনের অডিও স্ক্রিপ্ট"
}}
"""
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a senior agricultural advisor in Bangladesh. Respond only in JSON with Bengali text."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.3
                )
                return json.loads(response.choices[0].message.content)
            except Exception as e:
                logger.warning(f"[AgroAdvisoryAgent] OpenAI call failed: {e}. Using expert agronomy rulebase.")

        # অফলাইন / ডোমেন রুলবেস ফলব্যাক
        return self._agronomic_rulebase_advisory(district, crops, rain_sum, rain_prob, temp_max, wind)

    def _agronomic_rulebase_advisory(self, district: str, crops: List[str], rain_sum: float, rain_prob: int, temp_max: float, wind: float) -> Dict[str, Any]:
        crop_names = ", ".join(crops) if crops else "ফসল"
        
        # ১. ভারী বৃষ্টিপাত (> ২০ মিমি)
        if rain_sum >= 20.0 or rain_prob >= 75:
            return {
                "headline_bn": f"ভারী বৃষ্টির সতর্কতা ({district}): জমিতে পানি নিষ্কাশন নালা প্রস্তুত রাখুন",
                "risk_level": "high",
                "dos_bn": [
                    f"{crop_names} ক্ষেতে বৃষ্টির অতিরিক্ত পানি জমে থাকা ঠেকাতে দ্রুত ড্রেনেজ নালা কেটে দিন।",
                    "পরিপক্ক সবজি বা ফসল থাকলে বৃষ্টির আগেই জমি থেকে তুলে শুকনো উঁচু জায়গায় রাখুন।",
                    "বৃষ্টি থেমে যাওয়ার পর রোগবালাই দমনে অনুমোদিত ছত্রাকনাশক স্প্রে করার প্রস্তুতি নিন।"
                ],
                "donts_bn": [
                    "বৃষ্টি চলাকালীন বা বৃষ্টির আগে জমিতে কোনো প্রকার ইউরিয়া সার প্রয়োগ করবেন না।",
                    "দমকা বাতাস ও বৃষ্টির মধ্যে গাছে কীটনাশক স্প্রে করবেন না, এতে কার্যকারিতা নষ্ট হবে।"
                ],
                "irrigation_advice_bn": "পর্যাপ্ত বৃষ্টিপাতের সম্ভাবনা থাকায় সব ধরনের সেচ প্রদান সম্পূর্ণ বন্ধ রাখুন।",
                "voice_script_bn": f"মনোযোগ দিয়ে শুনুন কৃষক ভাই। {district} এলাকায় ভারী বৃষ্টির সম্ভাবনা রয়েছে। আপনার {crop_names} ক্ষেতের পানি নিষ্কাশন নালা কেটে রাখুন এবং সেচ দেওয়া সম্পূর্ণ বন্ধ রাখুন।"
            }

        # ২. মাঝারি বৃষ্টি (৫ - ২০ মিমি)
        elif rain_sum >= 5.0 or rain_prob >= 50:
            return {
                "headline_bn": f"বৃষ্টির সম্ভাবনা ({district}): জমিতে সেচ স্থগিত রাখুন",
                "risk_level": "moderate",
                "dos_bn": [
                    f"{crop_names} ক্ষেতের স্বাভাবিক যত্ন নিন এবং মাটির আর্দ্রতা পর্যবেক্ষণ করুন।",
                    "বৃষ্টির পরপরই গাছের গোড়ায় পানি জমে থাকলে তা অপসারণের ব্যবস্থা করুন।"
                ],
                "donts_bn": [
                    "মেঘলা আকাশের সময় জমিতে রাসায়নিক সার ছিটাবেন না।",
                    "বৃষ্টির ঠিক পূর্ব মুহূর্তে স্প্রে করা থেকে বিরত থাকুন।"
                ],
                "irrigation_advice_bn": "বৃষ্টির সম্ভাবনা বিবেচনা করে জমিতে অতিরিক্ত সেচ দেওয়া থেকে বিরত থাকুন।",
                "voice_script_bn": f"{district} এলাকায় আজ বৃষ্টির সম্ভাবনা রয়েছে। তাই জমিতে বাড়তি পানি বা সেচ দেওয়া স্থগিত রাখুন।"
            }

        # ৩. তীব্র গরম / খরা (> ৩৫°C)
        elif temp_max >= 35.0:
            return {
                "headline_bn": f"তীব্র তাপপ্রবাহ ({district}): ফসলে পর্যাপ্ত আর্দ্রতা ও সেচ বজায় রাখুন",
                "risk_level": "moderate",
                "dos_bn": [
                    f"ধান ক্ষেতে ২-৩ ইঞ্চি পানি ধরে রাখুন যাতে শিকড় অতিরিক্ত গরমে নষ্ট না হয়।",
                    f"{crop_names} ক্ষেতে সকালে সূর্য ওঠার আগে অথবা বিকেলে তাপমাত্রা কমলে হালকা সেচ দিন।",
                    "সবজির জমিতে মালচিং (খড় বা শুকনো পাতা বিছিয়ে) দিয়ে মাটির আর্দ্রতা ধরে রাখুন।"
                ],
                "donts_bn": [
                    "দুপুরের কড়া রোদ ও অতিরিক্ত গরমে কোনো অবস্থাতেই জমিতে সেচ বা স্প্রে করবেন না।"
                ],
                "irrigation_advice_bn": "মাটিতে যাতে ফাটল না ধরে সেজন্য নিয়মিত পরিমিত সেচ বজায় রাখা অত্যন্ত জরুরি।",
                "voice_script_bn": f"কৃষক বন্ধু, আজ {district} এলাকায় প্রচণ্ড গরম পড়তে পারে। সকাল বা বিকেলে আপনার জমিতে পরিমিত সেচ দিন, দুপুরের কড়া রোদে সেচ দেবেন না।"
            }

        # ৪. অনুকূল স্বাভাবিক আবহাওয়া
        else:
            return {
                "headline_bn": f"অনুকূল আবহাওয়া ({district}): ফসলের নিয়মিত পরিচর্যা চালিয়ে যান",
                "risk_level": "low",
                "dos_bn": [
                    f"{crop_names} ক্ষেতে আগাছা পরিষ্কার এবং প্রয়োজনীয় নিড়ানি দিন।",
                    "ফসল বৃদ্ধির এই পর্যায়ে অনুমোদিত মাত্রায় সুষম সার ও পুষ্টি নিশ্চিত করুন।"
                ],
                "donts_bn": [
                    "অতিরিক্ত মাত্রায় বালাইনাশক প্রয়োগ করবেন না; কৃষি কর্মকর্তার পরামর্শ মেনে চলুন।"
                ],
                "irrigation_advice_bn": "মাটির আর্দ্রতা বুঝে প্রয়োজন অনুসারে নিয়মিত স্বাভাবিক সেচ দিন।",
                "voice_script_bn": f"আজ {district} এলাকায় আবহাওয়া সম্পূর্ণ অনুকূল রয়েছে। আপনার ফসলের নিয়মিত পরিচর্যা চালিয়ে যেতে পারেন।"
            }

agro_advisory_agent = AgroAdvisoryAgent()
