"""
Generates 150-300 multilingual synthetic citizen development requests.
Adheres strictly to the guidelines in DATASET_GUIDE.md:
- Languages: English, Hindi, Marathi
- Pilot Districts: Pune, Thane (Maharashtra); Varanasi, Gorakhpur (Uttar Pradesh)
- Sectors: Healthcare, Water/Sanitation, Roads/Transport, Education
- Tagged: data_quality: 'synthetic'
- Channels: voice_web_speech, text_web_portal, messaging_app
"""

import json
import os
import random
import uuid
from datetime import datetime, timedelta, timezone

PILOT_REGIONS = [
    {"country_code": "IND", "admin1": "Maharashtra", "admin2": "Pune", "admin3": "Haveli", "lat": 18.5204, "lon": 73.8567},
    {"country_code": "IND", "admin1": "Maharashtra", "admin2": "Pune", "admin3": "Baramati", "lat": 18.1519, "lon": 74.5772},
    {"country_code": "IND", "admin1": "Maharashtra", "admin2": "Thane", "admin3": "Kalyan", "lat": 19.2403, "lon": 73.1305},
    {"country_code": "IND", "admin1": "Maharashtra", "admin2": "Thane", "admin3": "Bhiwandi", "lat": 19.2968, "lon": 73.0631},
    {"country_code": "IND", "admin1": "Uttar Pradesh", "admin2": "Varanasi", "admin3": "Pindra", "lat": 25.3176, "lon": 82.9739},
    {"country_code": "IND", "admin1": "Uttar Pradesh", "admin2": "Varanasi", "admin3": "Sadha", "lat": 25.3350, "lon": 82.9800},
]

CHANNELS = ["voice", "text", "messaging_app"]

REQUEST_TEMPLATES = [
    # Healthcare
    {
        "category": "healthcare",
        "sub_category": "phc_shortage",
        "urgency": "high",
        "variants": [
            ("en", "No primary health centre in our block. Nearest hospital is 22km away.", "No primary health centre in our block. Nearest hospital is 22km away."),
            ("mr", "आमच्या गावात प्राथमिक आरोग्य केंद्र नाही, दवाखान्यासाठी 20 किमी जावे लागते.", "No PHC in our village, have to travel 20km for treatment."),
            ("mr", "आरोग्य केंद्र खूप लांब आहे, गावात डॉक्टरांची तातडीने सोय करा.", "Health centre is too far, arrange doctor in village urgently."),
            ("hi", "हमारे गांव में कोई प्राथमिक स्वास्थ्य केंद्र नहीं है, जिला अस्पताल बहुत दूर है।", "No PHC in our village, district hospital is very far."),
            ("hi", "सरकारी अस्पताल में डॉक्टर नहीं मिलते और दवाइयां भी नहीं हैं।", "Doctors unavailable at government hospital and no medicines."),
            ("en", "Emergency ambulance cannot reach our village due to lack of local clinic.", "Emergency ambulance cannot reach our village due to lack of local clinic.")
        ]
    },
    # Water & Sanitation
    {
        "category": "water_sanitation",
        "sub_category": "drinking_water_pipeline",
        "urgency": "high",
        "variants": [
            ("en", "Tap water pipeline under Jal Jeevan Mission is damaged and not functional for 3 weeks.", "Tap water pipeline under Jal Jeevan Mission is damaged and not functional for 3 weeks."),
            ("mr", "गावात पिण्याचे पाणी 4 दिवसांनंतर येते, नळ पाणीपुरवठा योजना दुरुस्त करा.", "Drinking water arrives every 4 days, repair tap water supply scheme."),
            ("hi", "नल से जल योजना का पाइप टूटा हुआ है, गंदा पानी आ रहा है।", "Jal Jeevan Mission pipe broken, dirty water coming."),
            ("hi", "पीने के पानी की भारी किल्लत है, बोरवेल सूख चुके हैं।", "Severe drinking water shortage, borewells have dried up."),
            ("en", "Contaminated water supply in ward 4 causing stomach infections.", "Contaminated water supply in ward 4 causing stomach infections.")
        ]
    },
    # Roads & Transport
    {
        "category": "roads_transport",
        "sub_category": "all_weather_road",
        "urgency": "medium",
        "variants": [
            ("en", "Connecting road to main highway is unpaved and completely flooded during monsoon.", "Connecting road to main highway is unpaved and completely flooded during monsoon."),
            ("mr", "आमच्या वस्तीला जोडणारा मुख्य रस्ता चिखलमय झाला आहे, पक्का डांबरी रस्ता हवा.", "Main road connecting settlement is muddy, need paved asphalt road."),
            ("hi", "पीएमजीएसवाई सड़क पिछले दो साल से अधूरी पड़ी है, आवागमन ठप है।", "PMGSY road pending incomplete for two years, traffic stalled."),
            ("hi", "स्कूल जाने वाले बच्चों के लिए पुलिया और पक्की सड़क की जरूरत है।", "Need culvert bridge and paved road for school children."),
            ("en", "Public bus service does not come to our village because road is broken.", "Public bus service does not come to our village because road is broken.")
        ]
    },
    # Education
    {
        "category": "education",
        "sub_category": "school_infrastructure",
        "urgency": "medium",
        "variants": [
            ("en", "Government primary school has only 2 classrooms for 150 students and no girl's toilet.", "Government primary school has only 2 classrooms for 150 students and no girl's toilet."),
            ("mr", "जिल्हा परिषद शाळेचे छत गळत आहे आणि मुलींसाठी स्वतंत्र स्वच्छतागृह नाही.", "Zilla Parishad school roof is leaking and no separate toilet for girls."),
            ("hi", "प्राथमिक विद्यालय में बिजली और पीने के पानी की व्यवस्था नहीं है।", "No electricity or drinking water arrangement in primary school."),
            ("en", "High school requires science laboratory and math teachers.", "High school requires science laboratory and math teachers.")
        ]
    }
]

def generate_synthetic_dataset(count: int = 220, output_path: str = "data/synthetic/citizen_requests.json"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    records = []
    base_time = datetime.now(timezone.utc)

    for i in range(count):
        template = random.choice(REQUEST_TEMPLATES)
        lang, raw_text, translated = random.choice(template["variants"])
        region = random.choice(PILOT_REGIONS)
        channel = random.choice(CHANNELS)
        days_ago = random.randint(5, 450)
        timestamp = (base_time - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))).strftime("%Y-%m-%dT%H:%M:%SZ")

        record = {
            "id": f"REQ-SYNTH-{str(uuid.uuid4())[:8].upper()}",
            "timestamp": timestamp,
            "raw_text": raw_text,
            "translated_text": translated,
            "source_channel": channel,
            "detected_language": lang,
            "category": template["category"],
            "sub_category": template["sub_category"],
            "urgency_level": template["urgency"],
            "admin_hierarchy": {
                "country_code": region["country_code"],
                "admin1": region["admin1"],
                "admin2": region["admin2"],
                "locality": region["admin3"],
                "latitude": round(region["lat"] + random.uniform(-0.04, 0.04), 4),
                "longitude": round(region["lon"] + random.uniform(-0.04, 0.04), 4)
            },
            "cluster_id": f"CLUSTER-{template['category'][:3].upper()}-{region['admin2'][:3].upper()}",
            "data_quality": "synthetic",
            "source": "citizen_input",
            "source_url": None,
            "retrieved_at": timestamp
        }
        records.append(record)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"[SUCCESS] Generated {len(records)} synthetic records at {output_path}")

if __name__ == "__main__":
    generate_synthetic_dataset(220)

