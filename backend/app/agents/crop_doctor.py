import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# সমৃদ্ধ কৃষি রোগতত্ত্ব ও সমাধান ডাটাবেস (BARI / BRRI মানদণ্ড)
DISEASE_KNOWLEDGE_BASE = {
    "ধান_ব্লাস্ট": {
        "crop": "ধান",
        "disease_name_bn": "ধানের ব্লাস্ট রোগ (Leaf & Neck Blast)",
        "pathogen": "ছত্রাক (Pyricularia oryzae)",
        "symptoms": "পাতায় চোখের আকৃতির মতো বাদামী বা ধূসর দাগ, দাগের চারপাশ গাঢ় বাদামী। শিষের গোড়ায় আক্রমণ করলে শিষ ভেঙে পড়ে ও ধান চিটা হয়।",
        "severity": "high",
        "chemical_treatment": "ট্রাইসাইক্লাজল ৭৫ ডব্লিউপি (যেমন ট্রুপার বা দিফা) প্রতি লিটার পানিতে ০.৭৫ গ্রাম অথবা নেটিভো ০.৬ গ্রাম মিশিয়ে ৭-১০ দিন পর পর দুইবার স্প্রে করুন।",
        "organic_treatment": "আক্রান্ত পাতা সংগ্রহ করে পুড়িয়ে ফেলুন। জমিতে অতিরিক্ত ইউরিয়া সার ব্যবহার বন্ধ রাখুন এবং বিঘাপ্রতি ৫ কেজি পটাশ সার উপরিপ্রয়োগ করুন।",
        "prevention": "ব্লাস্ট প্রতিরোধী জাত যেমন ব্রি ধান-২৮ এর বদলে ব্রি ধান-৮৯ বা ব্রি ধান-৯২ চাষ করুন।"
    },
    "ধান_মাজরা": {
        "crop": "ধান",
        "disease_name_bn": "ধানের হলুদ মাজরা পোকা (Yellow Stem Borer)",
        "pathogen": "কীটপতঙ্গ (Scirpophaga incertulas)",
        "symptoms": "কুশি অবস্থায় আক্রমণ করলে মাঝের পাতা শুকিয়ে যায় যা 'মরা ডিগ' নামে পরিচিত। শিষ আসার পর আক্রমণ করলে সম্পূর্ণ শিষ সাদা চিটা হয়ে যায় যা 'সাদা শিষ' বলে।",
        "severity": "moderate",
        "chemical_treatment": "বিঘাপ্রতি ১ কেজি কার্বোফুরান ৫জি (যেমন ফুরাডান) অথবা কারটাপ (যেমন সানটাপ ৫০ এসপি) প্রতি লিটার পানিতে ২ গ্রাম মিশিয়ে স্প্রে করুন।",
        "organic_treatment": "জমিতে ডালপালা পুঁতে পার্চিং (পাখি বসার ব্যবস্থা) করুন যাতে পাখিরা পোকা ও মথ খেয়ে ফেলে। আলোক ফাঁদ ব্যবহার করুন।",
        "prevention": "চারা রোপণের সময় পাতার ডগা কেটে রোপণ করুন যাতে পোকার ডিম নষ্ট হয়।"
    },
    "আলু_নাবী_ধসা": {
        "crop": "আলু",
        "disease_name_bn": "আলুর নাবী ধসা / লেট ব্লাইট (Late Blight)",
        "pathogen": "ছত্রাক (Phytophthora infestans)",
        "symptoms": "কুয়াশাচ্ছন্ন আবহাওয়ায় পাতার ডগায় বা কিনারায় জলছাপের মতো ভেজা দাগ। দ্রুত পাতা কালো হয়ে পচে যায় এবং মিষ্টি পচা গন্ধ বের হয়। কয়েকদিনে সম্পূর্ণ জমি পুড়ে যাওয়ার মতো দেখায়।",
        "severity": "severe",
        "chemical_treatment": "আক্রমণ শুরু হওয়ার সাথে সাথে সিকিউর বা রিডোমিল গোল্ড ২ গ্রাম/লিটার অথবা মেলোডি ডিও ২ গ্রাম/লিটার হারে ৫-৭ দিন পর পর স্প্রে করুন। কুয়াশা থাকলে ম্যানকোজেব স্প্রে করে গাছ ভিজিয়ে রাখুন।",
        "organic_treatment": "আক্রান্ত গাছ দ্রুত তুলে গর্ত করে পুঁতে ফেলুন। সেচ দেওয়া সম্পূর্ণ বন্ধ রাখুন।",
        "prevention": "রোগমুক্ত প্রত্যয়িত বীজ ব্যবহার করুন এবং কুয়াশার পূর্বাভাস থাকলে আগেই সতর্কতামূলক স্প্রে করুন।"
    },
    "পেঁয়াজ_পার্পল_ব্লচ": {
        "crop": "পেঁয়াজ",
        "disease_name_bn": "পেঁয়াজের পার্পল ব্লচ / বেগুনি দাগ রোগ",
        "pathogen": "ছত্রাক (Alternaria porri)",
        "symptoms": "পাতায় ছোট ছোট বসে যাওয়া সাদাটে দাগ হয় যা পরবর্তীতে বেগুনি রঙ ধারণ করে। দাগগুলো বড় হয়ে পাতা ভেঙে পড়ে এবং পেঁয়াজের আকার ছোট হয়।",
        "severity": "moderate",
        "chemical_treatment": "রোভরাল ৫০ ডব্লিউপি অথবা ডায়াথেন এম-৪৫ প্রতি লিটার পানিতে ২ গ্রাম হারে আঠা (ট্রিটন/স্প্রেডার) মিশিয়ে ১০-১২ দিন পর পর ২-৩ বার স্প্রে করুন।",
        "organic_treatment": "জমিতে পানি নিষ্কাশন ভালো রাখুন। ট্রাইকোডার্মা বা জৈব ছত্রাকনাশক ব্যবহার করুন।",
        "prevention": "বীজ শোধন করে রোপণ করুন এবং শস্যপর্যায় অবলম্বন করুন।"
    },
    "বেগুন_ডগা_ছিদ্রকারী": {
        "crop": "বেগুন",
        "disease_name_bn": "বেগুনের ডগা ও ফল ছিদ্রকারী পোকা",
        "pathogen": "পোকা (Leucinodes orbonalis)",
        "symptoms": "পোকার কীড়া কচি ডগায় ছিদ্র করে ভেতরে ঢোকে, ফলে ডগা ঢলে পড়ে শুকিয়ে যায়। বেগুনের গায়ে ছোট ছিদ্র ও মল দেখা যায়।",
        "severity": "high",
        "chemical_treatment": "এমামেকটিন বেনজোয়েট (যেমন প্রোক্লেইম) প্রতি লিটার পানিতে ১ গ্রাম অথবা স্পিনোসাড (যেমন ট্রেসার) ০.৪ মিলি হারে মিশিয়ে স্প্রে করুন।",
        "organic_treatment": "ফেরোমোন ফাঁদ (Sex Pheromone Trap) প্রতি ৩ শতকে একটি করে পাতুন। আক্রান্ত ডগা হাত দিয়ে ভেঙে নষ্ট করুন।",
        "prevention": "একই জমিতে বারবার বেগুন চাষ না করে অন্য ফসল চাষ করুন।"
    }
}

class CropDoctor:
    """
    AI Crop Doctor Engine.
    Diagnoses crop diseases from symptoms, offers instant treatment prescriptions and prevention plans.
    """

    def diagnose_crop_issue(self, crop: str, symptom_keyword: str) -> Dict[str, Any]:
        crop_clean = crop.strip()
        symp_clean = symptom_keyword.strip().lower()

        # ম্যাচিং খোঁজা
        matched_key = None
        for key, data in DISEASE_KNOWLEDGE_BASE.items():
            if data["crop"] in crop_clean:
                if any(w in symp_clean for w in ["পোকা", "মাজরা", "ছিদ্র"]) and "মাজরা" in key or "ছিদ্র" in key:
                    matched_key = key
                    break
                elif any(w in symp_clean for w in ["ব্লাইট", "ধসা", "পচা", "কালো", "দাগ"]) and ("ধসা" in key or "ব্লাস্ট" in key or "ব্লচ" in key):
                    matched_key = key
                    break
                else:
                    matched_key = key # ঐ ফসলের ডিফল্ট প্রধান রোগ

        if not matched_key:
            # ফলব্যাক যদি স্পেসিফিক না মেলে
            matched_key = "আলু_নাবী_ধসা" if "আলু" in crop_clean else "ধান_ব্লাস্ট"

        record = DISEASE_KNOWLEDGE_BASE[matched_key]
        return {
            "status": "success",
            "crop": record["crop"],
            "disease_name": record["disease_name_bn"],
            "pathogen": record["pathogen"],
            "severity": record["severity"],
            "symptoms": record["symptoms"],
            "prescription": {
                "chemical": record["chemical_treatment"],
                "organic": record["organic_treatment"],
                "prevention": record["prevention"]
            }
        }

    def get_sample_diseases(self) -> List[Dict[str, Any]]:
        return [
            {"id": k, "crop": v["crop"], "name": v["disease_name_bn"], "severity": v["severity"]}
            for k, v in DISEASE_KNOWLEDGE_BASE.items()
        ]

crop_doctor = CropDoctor()
