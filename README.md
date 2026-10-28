# 🌾 কৃষাণ (Kishan) - AI Agro-Intelligence Platform

বাংলাদেশের কৃষকদের জন্য এআই চালিত দৈনিক বাজারদর, আবহাওয়া সতর্কতা, বাংলা ভয়েস ও কৃষি পরামর্শ প্ল্যাটফর্ম (Phase 1 MVP)।

---

## 🚀 প্রধান ফিচারসমূহ (Phase 1 MVP)

1. **দৈনিক হালনাগাদ বাজারদর (পাইকারি ও খুচরা রেট)**:
   - সরকারি কৃষি বিপণন অধিদপ্তর (DAM) ও এআই সার্চ এজেন্টের মাধ্যমে দেশের শীর্ষ মোকাম ও জেলাগুলোর বাজারদর।
   - পাইকারি দর (Wholesale) এবং খুচরা দর (Retail) এর স্পষ্ট তুলনা।
   - মূল্য পরিবর্তনের শতকরা হার ও ট্রেন্ড (📈 বৃদ্ধি, 📉 হ্রাস, ➖ অপরিবর্তিত)।
   - মধ্যস্বত্বভোগীদের সাথে দর কষাকষির জন্য এআই পরামর্শ।

2. **হাইপার-লোকাল আবহাওয়া ও এগ্রো-এডভাইজরি (Open-Meteo & OpenAI)**:
   - জেলাভিত্তিক রিয়েলটাইম আবহাওয়া ও ৭ দিনের পূর্বাভাস (তাপমাত্রা, বৃষ্টিপাত mm, আর্দ্রতা, বাতাসের গতি)।
   - কৃষকের নির্বাচিত ফসল (যেমন ধান, আলু, পেঁয়াজ, মরিচ) ও আবহাওয়া মিলিয়ে **কী করবেন (করণীয়)** এবং **কী করবেন না (বর্জনীয়)**।
   - সেচ ও সার প্রয়োগের সুনির্দিষ্ট পরামর্শ।

3. **ইন-অ্যাপ বাংলা ভয়েস স্পিকার (Text-to-Speech 🔊)**:
   - প্রতিটি ফসলের কার্ডে স্পিকারে ট্যাপ করলেই বাংলায় কথা বলে দাম জানিয়ে দেওয়া হয়।
   - এক ক্লিকে সম্পূর্ণ আবহাওয়া পূর্বাভাস ও কৃষি পরামর্শ শুনে বোঝার সুবিধা।

4. **জরুরি আবহাওয়া ও বাজার এসএমএস (SMS Gateway)**:
   - প্লাগেবল SMS গেটওয়ে (Mock, Greenweb BD, Twilio) যা জরুরি বৃষ্টিপাত বা প্রাকৃতিক দুর্যোগে কৃষকের ফোনে সরাসরি বাংলা এসএমএস পাঠায়।

5. **সহজ অনবোর্ডিং (পাসওয়ার্ডহীন গেস্ট মোড)**:
   - কোনো পাসওয়ার্ড বা জটিল ভেরিফিকেশন নেই।
   - জেলা, উপজেলা এবং পছন্দের ফসল নির্বাচন করলেই অফলাইনেও ব্যবহারের উপযোগী লোকাল ক্যাশ তৈরি হয়।

6. **মোবাইল ও ওয়েব ডুয়েল সাপোর্ট**:
   - **Flutter Android App**: সরাসরি ডিভাইসে ইনস্টলযোগ্য অ্যান্ড্রয়েড অ্যাপ্লিকেশন।
   - **Mobile-Responsive Web App (PWA)**: যেকোনো স্মার্টফোন ব্রাউজার থেকে তাৎক্ষণিক ব্যবহারের উপযোগী।

---

## 📂 প্রোজেক্ট স্ট্রাকচার

```
Kishan/
├── backend/                  # Python FastAPI ব্যাকএন্ড ও এআই ইঞ্জিন
│   ├── app/
│   │   ├── config.py         # এনভায়রনমেন্ট কনফিগারেশন
│   │   ├── database.py       # SQLAlchemy ও SQLite ডেটাবেস
│   │   ├── seed_data.py      # বাংলাদেশ ৬৪ জেলা ও কৃষি পণ্যের সিডার
│   │   ├── scheduler.py      # দৈনিক ০৬:০০ AM অটোমেটিক সিঙ্ক শিডিউলার
│   │   ├── main.py           # FastAPI অ্যাপ্লিকেশন এন্ট্রি পয়েন্ট
│   │   ├── models/           # DB Models (Commodity, Weather, Farmer, Alert)
│   │   ├── scrapers/         # DAM (dam.gov.bd) মার্কেট স্ক্র্যাপার
│   │   ├── agents/           # OpenAI বাজারদর ও এগ্রো-এডভাইজরি এআই এজেন্ট
│   │   ├── services/         # Weather, TTS Voice, SMS Gateway, Bazar Logic
│   │   ├── api/v1/           # REST API Routers
│   │   └── static/           # মোবাইল-রেসপন্সিভ ওয়েব UI (HTML/CSS/JS)
│   ├── tests/                # অটোমেটেড Pytest টেস্ট সুইট (১৩টি টেস্ট)
│   └── requirements.txt
│
└── kishan_app/               # Flutter অ্যান্ড্রয়েড মোবাইল অ্যাপ্লিকেশন
    ├── pubspec.yaml
    ├── lib/
    │   ├── main.dart
    │   ├── models/           # Commodity, Weather, FarmerProfile
    │   ├── services/         # ApiService, AudioService (TTS)
    │   ├── screens/          # Home, Bazar, Weather, Profile Screens
    │   └── widgets/          # CommodityCard
    └── android/              # AndroidManifest & build configs
```

---

## 🛠️ ব্যাকএন্ড রান করার নিয়ম

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **ওয়েব অ্যাপ (ব্রাউজার প্রিভিউ)**: [http://localhost:8000](http://localhost:8000)
- **ইন্টারেক্টিভ এপিআই ডক্স (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 অটোমেটেড টেস্ট রান করার নিয়ম

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

---

## 📱 ফ্লুটার মোবাইল অ্যাপ রান করার নিয়ম

```bash
cd kishan_app
flutter pub get
flutter run
```
