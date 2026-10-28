from datetime import date, timedelta
from app.database import Base, engine, SessionLocal
from app.models.commodity import CommodityPrice
from app.models.weather import WeatherRecord
from app.models.farmer import FarmerProfile

# বাংলাদেশের প্রধান জেলা ও ভৌগোলিক তথ্য
DISTRICTS_DATA = {
    "বগুড়া": {"lat": 24.8465, "lon": 89.3777, "division": "রাজশাহী", "market": "মহাস্থানগড় পাইকারি মোকাম"},
    "ঢাকা": {"lat": 23.8103, "lon": 90.4125, "division": "ঢাকা", "market": "কাওরান বাজার পাইকারি আড়ত"},
    "রাজশাহী": {"lat": 24.3636, "lon": 88.6241, "division": "রাজশাহী", "market": "বানেশ্বর হাট"},
    "যশোর": {"lat": 23.1664, "lon": 89.2081, "division": "খুলনা", "market": "বারোবাজার পাইকারি মোকাম"},
    "দিনাজপুর": {"lat": 25.6279, "lon": 88.6332, "division": "রংপুর", "market": "রানীরবন্দর পাইকারি বাজার"},
    "রংপুর": {"lat": 25.7439, "lon": 89.2752, "division": "রংপুর", "market": "সিটি বাজার পাইকারি মোকাম"},
    "ময়মনসিংহ": {"lat": 24.7471, "lon": 90.4203, "division": "ময়মনসিংহ", "market": "মেছুয়া বাজার"},
    "কুমিল্লা": {"lat": 23.4682, "lon": 91.1788, "division": "চট্টগ্রাম", "market": "চকবাজার পাইকারি আড়ত"},
    "চট্টগ্রাম": {"lat": 22.3569, "lon": 91.7832, "division": "চট্টগ্রাম", "market": "রিয়াজউদ্দিন বাজার"},
    "সিলেট": {"lat": 24.8949, "lon": 91.8687, "division": "সিলেট", "market": "সুভানীঘাট পাইকারি বাজার"},
    "বরিশাল": {"lat": 22.7010, "lon": 90.3535, "division": "বরিশাল", "market": "পোর্ট রোড পাইকারি মোকাম"},
    "খুলনা": {"lat": 22.8456, "lon": 89.5403, "division": "খুলনা", "market": "বড় বাজার পাইকারি মোকাম"},
    "মেহেরপুর": {"lat": 23.7719, "lon": 88.6322, "division": "খুলনা", "market": "বারাদী পাইকারি হাট"},
    "কুষ্টিয়া": {"lat": 23.9013, "lon": 89.1205, "division": "খুলনা", "market": "পোড়াদহ হাট"},
    "পাবনা": {"lat": 24.0064, "lon": 89.2372, "division": "রাজশাহী", "market": "ঈশ্বরদী পাইকারি আড়ত"},
    "টাঙ্গাইল": {"lat": 24.2513, "lon": 89.9167, "division": "ঢাকা", "market": "করটিয়া হাট"},
    "ফরিদপুর": {"lat": 23.6071, "lon": 89.8429, "division": "ঢাকা", "market": "হাজীগঞ্জ হাট"},
    "নাটোর": {"lat": 24.4206, "lon": 89.0003, "division": "রাজশাহী", "market": "তেবাড়িয়া হাট"}
}

# স্ট্যান্ডার্ড পণ্য তালিকা ও বেস প্রাইস (টাকা/কেজি)
COMMODITY_CATALOG = [
    # সবজি
    {"bn": "গোল আলু", "en": "Potato (Round)", "cat": "সবজি", "w_min": 26, "w_max": 29, "r_min": 32, "r_max": 36, "unit": "কেজি", "trend": "stable", "pct": 0.0},
    {"bn": "ডায়মন্ড আলু", "en": "Diamond Potato", "cat": "সবজি", "w_min": 28, "w_max": 31, "r_min": 35, "r_max": 38, "unit": "কেজি", "trend": "up", "pct": 3.4},
    {"bn": "বেগুন (গোল)", "en": "Eggplant (Round)", "cat": "সবজি", "w_min": 45, "w_max": 52, "r_min": 60, "r_max": 70, "unit": "কেজি", "trend": "down", "pct": -5.1},
    {"bn": "টমেটো (পাকা)", "en": "Tomato (Ripe)", "cat": "সবজি", "w_min": 50, "w_max": 58, "r_min": 65, "r_max": 75, "unit": "কেজি", "trend": "up", "pct": 6.8},
    {"bn": "ফুলকপি", "en": "Cauliflower", "cat": "সবজি", "w_min": 30, "w_max": 35, "r_min": 40, "r_max": 48, "unit": "পিস", "trend": "stable", "pct": 0.0},
    {"bn": "কাঁচা মরিচ", "en": "Green Chili", "cat": "সবজি", "w_min": 110, "w_max": 130, "r_min": 150, "r_max": 180, "unit": "কেজি", "trend": "up", "pct": 12.5},
    {"bn": "পটল", "en": "Pointed Gourd", "cat": "সবজি", "w_min": 35, "w_max": 42, "r_min": 48, "r_max": 55, "unit": "কেজি", "trend": "stable", "pct": 0.0},
    {"bn": "শসা", "en": "Cucumber", "cat": "সবজি", "w_min": 38, "w_max": 45, "r_min": 50, "r_max": 60, "unit": "কেজি", "trend": "down", "pct": -4.2},
    {"bn": "লাউ", "en": "Bottle Gourd", "cat": "সবজি", "w_min": 35, "w_max": 45, "r_min": 50, "r_max": 65, "unit": "পিস", "trend": "stable", "pct": 0.0},
    {"bn": "মিষ্টি কুমড়া", "en": "Sweet Pumpkin", "cat": "সবজি", "w_min": 25, "w_max": 30, "r_min": 35, "r_max": 42, "unit": "কেজি", "trend": "down", "pct": -2.8},
    
    # চাল ও ডাল
    {"bn": "ব্রি ধান-২৮", "en": "BRRI Dhan-28 (Paddy)", "cat": "চাল-ডাল", "w_min": 32, "w_max": 34, "r_min": 36, "r_max": 39, "unit": "কেজি", "trend": "stable", "pct": 0.0},
    {"bn": "ব্রি ধান-২৯", "en": "BRRI Dhan-29 (Paddy)", "cat": "চাল-ডাল", "w_min": 31, "w_max": 33, "r_min": 35, "r_max": 38, "unit": "কেজি", "trend": "stable", "pct": 0.0},
    {"bn": "মিনিকেট চাল", "en": "Miniket Rice", "cat": "চাল-ডাল", "w_min": 68, "w_max": 72, "r_min": 74, "r_max": 78, "unit": "কেজি", "trend": "up", "pct": 1.5},
    {"bn": "নাজিরশাইল চাল", "en": "Nazirshail Rice", "cat": "চাল-ডাল", "w_min": 72, "w_max": 78, "r_min": 80, "r_max": 88, "unit": "কেজি", "trend": "stable", "pct": 0.0},
    {"bn": "স্বর্ণা চাল (মোটা)", "en": "Swarna Rice", "cat": "চাল-ডাল", "w_min": 48, "w_max": 51, "r_min": 53, "r_max": 56, "unit": "কেজি", "trend": "down", "pct": -1.2},
    {"bn": "দেশি মসুর ডাল", "en": "Local Lentil (Masur)", "cat": "চাল-ডাল", "w_min": 125, "w_max": 132, "r_min": 140, "r_max": 150, "unit": "কেজি", "trend": "stable", "pct": 0.0},
    {"bn": "মুগ ডাল", "en": "Mung Bean", "cat": "চাল-ডাল", "w_min": 135, "w_max": 145, "r_min": 155, "r_max": 170, "unit": "কেজি", "trend": "up", "pct": 2.1},
    
    # মসলা
    {"bn": "দেশি পেঁয়াজ", "en": "Local Onion", "cat": "মসলা", "w_min": 75, "w_max": 82, "r_min": 88, "r_max": 98, "unit": "কেজি", "trend": "down", "pct": -6.5},
    {"bn": "ভারতীয় পেঁয়াজ", "en": "Imported Onion", "cat": "মসলা", "w_min": 68, "w_max": 74, "r_min": 78, "r_max": 85, "unit": "কেজি", "trend": "down", "pct": -4.0},
    {"bn": "দেশি রসুন", "en": "Local Garlic", "cat": "মসলা", "w_min": 170, "w_max": 185, "r_min": 200, "r_max": 220, "unit": "কেজি", "trend": "up", "pct": 4.8},
    {"bn": "আদা (দেশি)", "en": "Ginger (Local)", "cat": "মসলা", "w_min": 190, "w_max": 210, "r_min": 230, "r_max": 260, "unit": "কেজি", "trend": "stable", "pct": 0.0},
    {"bn": "শুকনো মরিচ", "en": "Dry Chili", "cat": "মসলা", "w_min": 340, "w_max": 380, "r_min": 400, "r_max": 450, "unit": "কেজি", "trend": "stable", "pct": 0.0},
    
    # তৈলবীজ
    {"bn": "সরিষার বীজ", "en": "Mustard Seed", "cat": "তৈলবীজ", "w_min": 80, "w_max": 88, "r_min": 95, "r_max": 105, "unit": "কেজি", "trend": "stable", "pct": 0.0},
    {"bn": "সরিষার খাঁটি তেল", "en": "Mustard Oil", "cat": "তৈলবীজ", "w_min": 210, "w_max": 230, "r_min": 240, "r_max": 260, "unit": "কেজি", "trend": "up", "pct": 1.8},
    
    # ফল
    {"bn": "কলা (সবরি)", "en": "Banana (Sobri)", "cat": "ফল", "w_min": 35, "w_max": 42, "r_min": 48, "r_max": 60, "unit": "হালি", "trend": "stable", "pct": 0.0},
    {"bn": "পেয়ারা", "en": "Guava", "cat": "ফল", "w_min": 50, "w_max": 60, "r_min": 70, "r_max": 85, "unit": "কেজি", "trend": "down", "pct": -3.5}
]

def seed_database(force: bool = False):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        today = date.today()
        existing_count = db.query(CommodityPrice).count()
        if existing_count > 0 and not force:
            print(f"[Seed] Database already contains {existing_count} commodity records. Skipping seed.")
            return

        # ডিস্ট্রিক্ট ও কমোডিটি অনুযায়ী ডেটা পপুলেট
        print(f"[Seed] Seeding commodity prices for {len(DISTRICTS_DATA)} districts...")
        
        # জেলা অনুযায়ী স্থানীয় মূল্যের বৈচিত্র্য ফ্যাক্টর (যেমন ঢাকা একটু বেশি, বগুড়া/যশোরে কম)
        district_multipliers = {
            "ঢাকা": 1.15,
            "চট্টগ্রাম": 1.12,
            "সিলেট": 1.10,
            "বগুড়া": 0.92,
            "যশোর": 0.94,
            "দিনাজপুর": 0.90,
            "মেহেরপুর": 0.91,
            "রাজশাহী": 0.93,
            "রংপুর": 0.91,
            "ময়মনসিংহ": 0.96,
            "বরিশাল": 1.02,
            "খুলনা": 0.98,
            "কুষ্টিয়া": 0.95,
            "পাবনা": 0.94,
            "টাঙ্গাইল": 0.98,
            "ফরিদপুর": 0.97,
            "নাটোর": 0.92,
            "কুমিল্লা": 1.04
        }

        records = []
        for dist_name, dist_info in DISTRICTS_DATA.items():
            mult = district_multipliers.get(dist_name, 1.0)
            
            for item in COMMODITY_CATALOG:
                w_min = round(item["w_min"] * mult, 1)
                w_max = round(item["w_max"] * mult, 1)
                w_avg = round((w_min + w_max) / 2, 1)
                
                r_min = round(item["r_min"] * mult, 1)
                r_max = round(item["r_max"] * mult, 1)
                r_avg = round((r_min + r_max) / 2, 1)
                
                record = CommodityPrice(
                    name_bn=item["bn"],
                    name_en=item["en"],
                    category=item["cat"],
                    district=dist_name,
                    market_name=dist_info["market"],
                    wholesale_min=w_min,
                    wholesale_max=w_max,
                    wholesale_avg=w_avg,
                    retail_min=r_min,
                    retail_max=r_max,
                    retail_avg=r_avg,
                    unit=item["unit"],
                    price_date=today,
                    price_trend=item["trend"],
                    price_change_pct=item["pct"],
                    source="dam"
                )
                records.append(record)
                
        db.bulk_save_objects(records)
        db.commit()
        print(f"[Seed] Successfully seeded {len(records)} commodity records.")

        # আবহাওয়া ও এগ্রো-এডভাইজরি রেকর্ড সিডিং
        weather_records = []
        for dist_name, dist_info in DISTRICTS_DATA.items():
            # ডেমো সতর্কবার্তা ও এডভাইজরি
            dos = "১. জমিতে জমে থাকা অতিরিক্ত পানি নিষ্কাশনের নালা কেটে দিন।\n২. বৃষ্টির পরপরই রোগবালাই দমনে অনুমোদিত ছত্রাকনাশক স্প্রে করুন।\n৩. পরিপক্ক সবজি দ্রুত সংগ্রহ করে শুকনো স্থানে সংরক্ষণ করুন।"
            donts = "১. মেঘলা বা বৃষ্টির আবহাওয়ায় জমিতে ইউরিয়া সার প্রয়োগ করবেন না।\n২. বাতাস ও বৃষ্টির সময় স্প্রে করা থেকে বিরত থাকুন।"
            irrig = "আগামী ২ দিন বৃষ্টির সম্ভাবনা থাকায় কোনো প্রকার সেচ প্রদান সম্পূর্ণ বন্ধ রাখুন।"
            
            w_rec = WeatherRecord(
                district=dist_name,
                date=today,
                temp_max=31.5,
                temp_min=24.0,
                precipitation_sum=18.5,
                precipitation_prob=75,
                humidity=82,
                wind_speed=14.2,
                weather_condition="বিক্ষিপ্ত বৃষ্টিপাত ও বজ্রপাত",
                risk_level="moderate",
                advisory_headline_bn="বৃষ্টিপাত সতর্কতা: জমিতে পানি নিষ্কাশন নিশ্চিত করুন এবং সেচ স্থগিত রাখুন",
                advisory_dos_bn=dos,
                advisory_donts_bn=donts,
                irrigation_advice_bn=irrig,
                target_crops="ধান,আলু,সবজি,মরিচ"
            )
            weather_records.append(w_rec)

        db.bulk_save_objects(weather_records)
        db.commit()
        print(f"[Seed] Successfully seeded {len(weather_records)} weather and advisory records.")

        # ডিফল্ট ডেমো প্রোফাইল
        demo_farmer = FarmerProfile(
            device_id="demo-farmer-01",
            name="করিম মিয়া",
            phone="01712345678",
            district="বগুড়া",
            upazila="শিবগঞ্জ",
            favorite_crops="ধান,আলু,কাঁচা মরিচ"
        )
        db.add(demo_farmer)
        db.commit()
        print("[Seed] Seed completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"[Seed] Error seeding data: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database(force=True)
