import csv
import random
import uuid
import os
from datetime import datetime, timedelta

# Create the data folder if it doesn't exist
os.makedirs(os.path.join("backend", "data"), exist_ok=True)

# Define constants
NEIGHBORHOODS = {
    "Kasba": {"lat": (22.515, 22.525), "lon": (88.380, 88.390), "wards": [91, 92]},
    "Gariahat": {"lat": (22.515, 22.522), "lon": (88.365, 88.375), "wards": [85, 86]},
    "Jadavpur": {"lat": (22.490, 22.505), "lon": (88.360, 88.375), "wards": [92, 93, 96, 99]},
    "Salt Lake": {"lat": (22.565, 22.595), "lon": (88.405, 88.435), "wards": [28, 30, 31, 32, 33]},
    "Behala": {"lat": (22.485, 22.505), "lon": (88.305, 88.325), "wards": [118, 119, 120, 121]},
    "Park Circus": {"lat": (22.538, 22.548), "lon": (88.365, 88.375), "wards": [60, 64, 65]},
    "Howrah": {"lat": (22.575, 22.595), "lon": (88.320, 88.340), "wards": [15, 16, 20, 21]},
    "Lake Market": {"lat": (22.508, 22.515), "lon": (88.345, 88.353), "wards": [87, 88, 90]},
    "New Town": {"lat": (22.570, 22.595), "lon": (88.445, 88.475), "wards": [101, 102, 103]},
    "Shyambazar": {"lat": (22.595, 22.605), "lon": (88.365, 88.375), "wards": [10, 11, 12]},
    "Alipore": {"lat": (22.525, 22.535), "lon": (88.325, 88.335), "wards": [74, 82]},
    "Ballygunge": {"lat": (22.522, 22.535), "lon": (88.360, 88.370), "wards": [68, 69, 72]},
    "Bowbazar": {"lat": (22.562, 22.572), "lon": (88.352, 88.362), "wards": [47, 48]},
    "Tangra": {"lat": (22.545, 22.555), "lon": (88.382, 88.395), "wards": [57, 58]},
    "Tollygunge": {"lat": (22.480, 22.495), "lon": (88.340, 88.350), "wards": [94, 95, 97, 98]}
}

CATEGORIES = {
    "Civic Observations": {
        "Streetlight Outage": {
            "descriptions": [
                "Streetlight not functioning on {street}, making the lane completely dark and unsafe for walkers.",
                "Multiple consecutive streetlights are flickering on {street}.",
                "Daytime burning of streetlights reported near {landmark} in {neighborhood}."
            ],
            "severity_weights": [0.3, 0.5, 0.1, 0.1],  # Low, Med, High, Critical
            "affected_groups": ["Pedestrians", "Local Residents"],
            "sentiment_range": (-0.7, -0.2),
            "wellbeing_range": (3.0, 6.0)
        },
        "Garbage Accumulation": {
            "descriptions": [
                "Overflowing community vats and garbage spilled onto the road near {landmark}.",
                "Plastic waste and dry leaves piled up on the corner of {street}.",
                "Illegal dumping of construction debris blocking the passage on {street}."
            ],
            "severity_weights": [0.2, 0.5, 0.25, 0.05],
            "affected_groups": ["Local Residents", "Pedestrians"],
            "sentiment_range": (-0.8, -0.4),
            "wellbeing_range": (4.0, 7.0)
        },
        "Pothole/Road Damage": {
            "descriptions": [
                "Large pothole in the middle of {street} posing a severe threat to two-wheelers.",
                "Caved-in road surface near {landmark} causing traffic bottlenecks.",
                "Uneven road surfaces and loose gravel after recent utility trenching on {street}."
            ],
            "severity_weights": [0.1, 0.4, 0.4, 0.1],
            "affected_groups": ["Commuters", "Pedestrians"],
            "sentiment_range": (-0.9, -0.3),
            "wellbeing_range": (5.0, 8.0)
        },
        "Stagnant Water": {
            "descriptions": [
                "Accumulated rainwater in a vacant plot near {landmark}, breeding ground for mosquitoes.",
                "Stagnant puddle near {street} footpath for over 4 days.",
                "Blocked gully pit causing water to pool around the local market area."
            ],
            "severity_weights": [0.2, 0.5, 0.2, 0.1],
            "affected_groups": ["Local Residents", "Children", "Elderly & Disabled"],
            "sentiment_range": (-0.7, -0.3),
            "wellbeing_range": (4.5, 7.5)
        }
    },
    "Friction Events": {
        "Traffic Congestion": {
            "descriptions": [
                "Severe bottleneck on {street} due to haphazard auto-rickshaw parking near {landmark}.",
                "Gridlock at {neighborhood} crossing during peak evening hours.",
                "Traffic crawl reported near {landmark} due to waterlogging."
            ],
            "severity_weights": [0.2, 0.5, 0.25, 0.05],
            "affected_groups": ["Commuters", "Vendors/Business Owners"],
            "sentiment_range": (-0.8, -0.3),
            "wellbeing_range": (3.5, 6.5)
        },
        "Encroached Sidewalk": {
            "descriptions": [
                "Footpath completely blocked by temporary stalls near {landmark}, forcing pedestrians to walk on the busy road.",
                "Construction materials dumped on the sidewalk of {street}.",
                "Shop extensions occupying major portion of the pedestrian walkway in {neighborhood}."
            ],
            "severity_weights": [0.3, 0.4, 0.2, 0.1],
            "affected_groups": ["Pedestrians", "Elderly & Disabled"],
            "sentiment_range": (-0.7, -0.2),
            "wellbeing_range": (4.0, 7.0)
        },
        "Illegal Parking": {
            "descriptions": [
                "Double parking of private vehicles on {street} restricting traffic flow to a single lane.",
                "Commercial trucks parked in a residential lane near {landmark} blocking building gates.",
                "Two-wheelers parked on the sidewalk near {neighborhood} Metro station."
            ],
            "severity_weights": [0.4, 0.4, 0.15, 0.05],
            "affected_groups": ["Commuters", "Local Residents"],
            "sentiment_range": (-0.6, -0.1),
            "wellbeing_range": (2.5, 5.5)
        },
        "Waterlogged Street": {
            "descriptions": [
                "Ankle-deep waterlogging on {street} after an hour of heavy rain.",
                "Knee-deep waterlogged road near {landmark} preventing vehicles from passing.",
                "Overflowing open drain flooding the side lanes of {neighborhood}."
            ],
            "severity_weights": [0.05, 0.25, 0.5, 0.2],
            "affected_groups": ["Commuters", "Local Residents", "Vendors/Business Owners"],
            "sentiment_range": (-0.95, -0.5),
            "wellbeing_range": (6.0, 9.5)
        }
    },
    "Community Actions": {
        "Cleanliness Drive": {
            "descriptions": [
                "Local youth group organized a cleanliness and garbage clearance drive at {landmark}.",
                "Neighborhood association cleaned up the trash pile near {street} and placed new dustbins.",
                "Citizen-led drive to clean and paint the walls near {neighborhood} park."
            ],
            "severity_weights": [0.8, 0.15, 0.05, 0.0],
            "affected_groups": ["Local Residents", "All Citizens"],
            "sentiment_range": (0.6, 0.95),
            "wellbeing_range": (7.0, 9.5)
        },
        "Tree Plantation": {
            "descriptions": [
                "Planted 50 saplings along the median divider of {street} under community initiative.",
                "Local residents tree plantation drive around {landmark} playground.",
                "Replaced uprooted trees with fresh native saplings in {neighborhood}."
            ],
            "severity_weights": [0.85, 0.1, 0.05, 0.0],
            "affected_groups": ["Local Residents", "Children"],
            "sentiment_range": (0.7, 0.98),
            "wellbeing_range": (7.5, 9.8)
        },
        "Neighborhood Watch": {
            "descriptions": [
                "Citizen group formed a night patrol team for the lanes around {street}.",
                "Community meeting organized to discuss security and CCTV installation near {landmark}.",
                "Safety awareness campaign conducted for senior citizens in {neighborhood}."
            ],
            "severity_weights": [0.7, 0.2, 0.1, 0.0],
            "affected_groups": ["Local Residents", "Elderly & Disabled"],
            "sentiment_range": (0.4, 0.8),
            "wellbeing_range": (6.5, 8.5)
        },
        "Public Wall Art/Paint": {
            "descriptions": [
                "Beautification of spit-stained public walls near {landmark} with local cultural art.",
                "Community art drive on the perimeter wall of {street} school.",
                "Volunteers painting street pillars to discourage illegal bill pasting."
            ],
            "severity_weights": [0.9, 0.1, 0.0, 0.0],
            "affected_groups": ["Local Residents", "Pedestrians"],
            "sentiment_range": (0.6, 0.9),
            "wellbeing_range": (6.0, 8.5)
        }
    },
    "Environmental Readings": {
        "Air Quality Warning": {
            "descriptions": [
                "AQI readings exceeded 250 (Poor) in the vicinity of {landmark}.",
                "High particulate matter (PM2.5) levels recorded near {street} transit corridor.",
                "Smog and dust accumulation lowering visibility and quality of air in {neighborhood}."
            ],
            "severity_weights": [0.1, 0.3, 0.45, 0.15],
            "affected_groups": ["Elderly & Disabled", "Children", "All Citizens"],
            "sentiment_range": (-0.8, -0.4),
            "wellbeing_range": (5.5, 8.5)
        },
        "Noise Pollution": {
            "descriptions": [
                "Loud speakers and DJ system operating past midnight near {landmark} violating residential limits.",
                "Continuous high-decibel honking on {street} near the silent zone (hospital).",
                "High noise level from generator sets operating at a commercial site in {neighborhood}."
            ],
            "severity_weights": [0.3, 0.4, 0.2, 0.1],
            "affected_groups": ["Local Residents", "Elderly & Disabled", "Children"],
            "sentiment_range": (-0.7, -0.3),
            "wellbeing_range": (4.0, 7.0)
        },
        "High Heat Index": {
            "descriptions": [
                "Severe heat index of 44C recorded. High risk of heat-stroke in non-shaded areas of {street}.",
                "Extreme afternoon temperature spike near {landmark} with zero canopy coverage.",
                "Urgent warnings for street vendors due to heat wave conditions in {neighborhood}."
            ],
            "severity_weights": [0.1, 0.4, 0.4, 0.1],
            "affected_groups": ["Vendors/Business Owners", "Commuters", "Elderly & Disabled"],
            "sentiment_range": (-0.7, -0.2),
            "wellbeing_range": (5.0, 8.0)
        },
        "Water Quality/Contamination": {
            "descriptions": [
                "Turbid/smelly tap water reported by multiple households near {landmark}.",
                "Leakage in municipal water pipe mixing with sewage line near {street}.",
                "Bacteriological contamination suspected in the local community tube well."
            ],
            "severity_weights": [0.05, 0.2, 0.5, 0.25],
            "affected_groups": ["Local Residents", "Children"],
            "sentiment_range": (-0.9, -0.4),
            "wellbeing_range": (6.5, 9.5)
        }
    },
    "Accessibility Issues": {
        "Broken Ramp/Sidewalk": {
            "descriptions": [
                "Broken wheelchair ramp at the entrance of public library/office near {landmark}.",
                "Damaged tactile paving on the sidewalk of {street} making it difficult for visually impaired.",
                "Missing slab on the footpath of {street} creating a dangerous open pit."
            ],
            "severity_weights": [0.1, 0.3, 0.45, 0.15],
            "affected_groups": ["Elderly & Disabled", "Pedestrians"],
            "sentiment_range": (-0.8, -0.3),
            "wellbeing_range": (5.0, 8.5)
        },
        "Obstruction on Pedestrian Path": {
            "descriptions": [
                "Low-hanging electric cables and internet wires over the footpath on {street}.",
                "Generator set parked right in the middle of the access ramp near {landmark}.",
                "Two-wheelers parked inside the pedestrian subway access gate in {neighborhood}."
            ],
            "severity_weights": [0.2, 0.5, 0.25, 0.05],
            "affected_groups": ["Elderly & Disabled", "Pedestrians"],
            "sentiment_range": (-0.7, -0.2),
            "wellbeing_range": (4.5, 7.5)
        },
        "Lack of Tactile Paving": {
            "descriptions": [
                "Newly constructed pedestrian pathway on {street} lacks tactile guiding tiles for the blind.",
                "Tactile pathway missing at the major intersection near {landmark}.",
                "Metro station access plaza lacks continuous guiding paths for disabled commuters."
            ],
            "severity_weights": [0.6, 0.3, 0.1, 0.0],
            "affected_groups": ["Elderly & Disabled"],
            "sentiment_range": (-0.5, -0.1),
            "wellbeing_range": (3.0, 6.0)
        },
        "Inoperable Public Elevator/Escalator": {
            "descriptions": [
                "Public escalator at the foot overbridge near {landmark} has been out of service for a week.",
                "Elevator at the transit hub on {street} is stuck and non-functional.",
                "Platform lift for disabled access at the metro entrance is locked and unusable."
            ],
            "severity_weights": [0.1, 0.3, 0.45, 0.15],
            "affected_groups": ["Elderly & Disabled", "Commuters"],
            "sentiment_range": (-0.8, -0.3),
            "wellbeing_range": (5.0, 8.0)
        }
    },
    "Neighborhood Momentum Signals": {
        "Active Community Campaign": {
            "descriptions": [
                "Over 200 citizens signed a petition for green spaces near {landmark}.",
                "Sustained neighborhood campaign to restore the heritage pond in {neighborhood}.",
                "Active social media campaign by residents of {street} to install speed breakers."
            ],
            "severity_weights": [0.7, 0.2, 0.1, 0.0],
            "affected_groups": ["Local Residents", "All Citizens"],
            "sentiment_range": (0.4, 0.8),
            "wellbeing_range": (5.5, 8.0)
        },
        "Local Youth Sports Event": {
            "descriptions": [
                "Community football tournament organized at {neighborhood} ground, drawing 500+ attendees.",
                "Inauguration of a street cricket championship near {landmark} to promote local engagement.",
                "Youth badminton league organized under the streetlights of {street} by community members."
            ],
            "severity_weights": [0.8, 0.15, 0.05, 0.0],
            "affected_groups": ["Children", "Local Residents"],
            "sentiment_range": (0.6, 0.95),
            "wellbeing_range": (6.5, 9.0)
        },
        "High Citizen App Engagement": {
            "descriptions": [
                "Spike in active civic reports from {neighborhood} showing high neighborhood vigilance.",
                "Over 100 resolved tickets upvoted by citizens near {landmark}.",
                "Collaborative mapping of accessibility barriers on {street} by local college volunteers."
            ],
            "severity_weights": [0.6, 0.3, 0.1, 0.0],
            "affected_groups": ["All Citizens", "Local Residents"],
            "sentiment_range": (0.5, 0.85),
            "wellbeing_range": (6.0, 8.5)
        },
        "Rapid Issue Resolution": {
            "descriptions": [
                "Pothole on {street} reported and patched within 12 hours under citizen monitoring.",
                "Garbage heap cleared and area sanitized near {landmark} in record time.",
                "Faulty streetlights restored within hours of citizen escalations on {street}."
            ],
            "severity_weights": [0.7, 0.2, 0.1, 0.0],
            "affected_groups": ["All Citizens", "Local Residents", "Commuters"],
            "sentiment_range": (0.7, 0.95),
            "wellbeing_range": (7.0, 9.5)
        }
    }
}

STREETS = [
    "Rashbehari Avenue", "Gariahat Road", "SP Mukherjee Road", "Hazra Road", "Jadavpur Central Road",
    "Raja SC Mullick Road", "Major Arterial Road", "Broad Street", "Park Street", "Shakespeare Sarani",
    "Grand Trunk Road", "Howrah Road", "Sarat Bose Road", "Southern Avenue", "EM Bypass",
    "Salt Lake Bypass", "Prince Anwar Shah Road", "Netaji Subhash Chandra Bose Road", "Bidhan Sarani",
    "Acharya Jagadish Chandra Bose Road", "VIP Road", "Jessore Road"
]

LANDMARKS = [
    "Metro Station", "Local Market", "Government School", "Public Park", "District Hospital",
    "Post Office", "Police Station", "Bus Terminus", "Community Hall", "Playground",
    "Crossing/Intersection", "Heritage Temple", "Public Library", "Shopping Complex"
]

SEVERITY_LEVELS = ["Low", "Medium", "High", "Critical"]
SOURCE_TYPES = ["Citizen App", "Sensor Network", "Field Volunteer", "Social Media Alert", "Municipal Feed"]

# Base time anchor (Current time in mock 2026-07-05)
NOW = datetime(2026, 7, 5, 21, 20, 15)
START_TIME = NOW - timedelta(days=90)

def generate_row():
    # 1. Neighborhood, lat, lon, ward
    neighborhood = random.choice(list(NEIGHBORHOODS.keys()))
    coords = NEIGHBORHOODS[neighborhood]
    lat = round(random.uniform(coords["lat"][0], coords["lat"][1]), 6)
    lon = round(random.uniform(coords["lon"][0], coords["lon"][1]), 6)
    ward = random.choice(coords["wards"])
    
    # 2. Category & Subcategory
    category = random.choice(list(CATEGORIES.keys()))
    subcategory = random.choice(list(CATEGORIES[category].keys()))
    sub_config = CATEGORIES[category][subcategory]
    
    # 3. Severity
    severity = random.choices(SEVERITY_LEVELS, weights=sub_config["severity_weights"])[0]
    
    # 4. Affected Group
    affected_group = random.choice(sub_config["affected_groups"])
    
    # 5. Description
    street = random.choice(STREETS)
    landmark = random.choice(LANDMARKS)
    desc_template = random.choice(sub_config["descriptions"])
    description = desc_template.format(street=street, landmark=landmark, neighborhood=neighborhood)
    
    # 6. Source Type
    # Sensor networks map to environmental readings usually, but can be others
    if category == "Environmental Readings":
        source_type = random.choices(SOURCE_TYPES, weights=[0.2, 0.6, 0.1, 0.05, 0.05])[0]
    else:
        source_type = random.choices(SOURCE_TYPES, weights=[0.6, 0.05, 0.2, 0.1, 0.05])[0]
        
    # 7. Timestamp (skewed towards daytime 7 AM - 10 PM)
    delta_seconds = random.randint(0, int((NOW - START_TIME).total_seconds()))
    timestamp_raw = START_TIME + timedelta(seconds=delta_seconds)
    
    # Adjust hour to make daytime more probable
    hour_adj = random.choices(
        list(range(24)),
        weights=[0.05, 0.02, 0.01, 0.01, 0.02, 0.05, 0.15, 0.3, 0.5, 0.6, 0.7, 0.8, 0.8, 0.8, 0.7, 0.6, 0.8, 0.9, 0.8, 0.6, 0.4, 0.2, 0.1, 0.08]
    )[0]
    timestamp = timestamp_raw.replace(hour=hour_adj, minute=random.randint(0, 59), second=random.randint(0, 59))
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # 8. Sentiment Score & Wellbeing Impact
    sentiment_min, sentiment_max = sub_config["sentiment_range"]
    sentiment_score = round(random.uniform(sentiment_min, sentiment_max), 2)
    # Severity adjustment
    if severity == "Critical":
        sentiment_score = max(-1.0, round(sentiment_score - 0.15, 2))
    elif severity == "Low" and sentiment_score < 0:
        sentiment_score = min(0.0, round(sentiment_score + 0.1, 2))
        
    wb_min, wb_max = sub_config["wellbeing_range"]
    wellbeing_impact = round(random.uniform(wb_min, wb_max), 1)
    if severity == "Critical":
        wellbeing_impact = min(10.0, round(wellbeing_impact + 1.2, 1))
    elif severity == "Low":
        wellbeing_impact = max(0.5, round(wellbeing_impact - 1.0, 1))
        
    # 9. Resolved
    # Older items are more likely to be resolved. Community actions / momentum signals are usually resolved = true
    age_days = (NOW - timestamp).days
    if category in ["Community Actions", "Neighborhood Momentum Signals"]:
        resolved = True
    else:
        # Probability of resolution depends on age and severity
        resolved_prob = min(0.95, 0.2 + (age_days / 90.0) * 0.75)
        if severity == "Critical":
            resolved_prob -= 0.15
        elif severity == "High":
            resolved_prob -= 0.05
        resolved = random.random() < resolved_prob
        
    # 10. Volunteer Count
    # Positive items or resolved items tend to have volunteers
    if category in ["Community Actions", "Neighborhood Momentum Signals"]:
        volunteer_count = random.randint(5, 45)
    elif resolved and severity in ["High", "Critical"]:
        volunteer_count = random.choices([0, random.randint(1, 15)], weights=[0.4, 0.6])[0]
    else:
        volunteer_count = random.choices([0, random.randint(1, 5)], weights=[0.9, 0.1])[0]
        
    # 11. Mission Created
    # Higher chance if severe, unresolved, or community-based, and not sensor-network
    if source_type == "Sensor Network":
        mission_created = False
    elif category in ["Community Actions", "Neighborhood Momentum Signals"]:
        mission_created = True
    else:
        mission_prob = 0.05
        if severity == "Critical":
            mission_prob = 0.6
        elif severity == "High":
            mission_prob = 0.35
        elif severity == "Medium":
            mission_prob = 0.1
        mission_created = random.random() < mission_prob
        
    # 12. Response Time Minutes
    if resolved:
        # Base response time depends on category & severity
        if severity == "Critical":
            response_time_minutes = random.randint(30, 240)
        elif severity == "High":
            response_time_minutes = random.randint(120, 1440)
        elif severity == "Medium":
            response_time_minutes = random.randint(480, 4320)
        else:
            response_time_minutes = random.randint(1440, 10080)
    else:
        response_time_minutes = ""
        
    # 13. AI Summary
    ai_summary = f"{subcategory} reported in {neighborhood} (Ward {ward}) affecting {affected_group.lower()}."
    if severity == "Critical" or severity == "High":
        ai_summary += f" Action required due to {severity.lower()} severity level."
        
    # 14. Event ID
    event_id = str(uuid.uuid4())
    
    return {
        "event_id": event_id,
        "timestamp": timestamp_str,
        "neighborhood": neighborhood,
        "ward": ward,
        "category": category,
        "subcategory": subcategory,
        "severity": severity,
        "affected_group": affected_group,
        "description": description,
        "source_type": source_type,
        "latitude": lat,
        "longitude": lon,
        "sentiment_score": sentiment_score,
        "wellbeing_impact": wellbeing_impact,
        "resolved": str(resolved).upper(),
        "volunteer_count": volunteer_count,
        "ai_summary": ai_summary,
        "mission_created": str(mission_created).upper(),
        "response_time_minutes": response_time_minutes
    }

def main():
    num_rows = 26500
    fields = [
        "event_id", "timestamp", "neighborhood", "ward", "category", "subcategory",
        "severity", "affected_group", "description", "source_type", "latitude",
        "longitude", "sentiment_score", "wellbeing_impact", "resolved", "volunteer_count",
        "ai_summary", "mission_created", "response_time_minutes"
    ]
    
    out_path = os.path.join("backend", "data", "owe_civic_dataset.csv")
    print(f"Generating {num_rows} rows of civic data to {out_path}...")
    
    with open(out_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        
        for i in range(num_rows):
            row = generate_row()
            writer.writerow(row)
            if (i + 1) % 5000 == 0:
                print(f"Generated {i + 1} rows...")
                
    print("Done!")

if __name__ == "__main__":
    main()
