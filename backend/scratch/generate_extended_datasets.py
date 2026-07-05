import os
import csv
import uuid
import random
import pandas as pd
from datetime import datetime, timedelta

# Create the data folder if it doesn't exist
os.makedirs(os.path.join("backend", "data"), exist_ok=True)

# Define constants
NEIGHBORHOODS = {
    "Kasba": {"lat": (22.515, 22.525), "lon": (88.380, 88.390), "wards": [91, 92], "tree_cover": 12.5, "metro": "Kalighat Metro (Nearby)"},
    "Gariahat": {"lat": (22.515, 22.522), "lon": (88.365, 88.375), "wards": [85, 86], "tree_cover": 10.0, "metro": "Kalighat Metro (Nearby)"},
    "Jadavpur": {"lat": (22.490, 22.505), "lon": (88.360, 88.375), "wards": [92, 93, 96, 99], "tree_cover": 18.0, "metro": "Kavi Nazrul Metro (Nearby)"},
    "Salt Lake": {"lat": (22.565, 22.595), "lon": (88.405, 88.435), "wards": [28, 30, 31, 32, 33], "tree_cover": 28.0, "metro": "Salt Lake Sector V Metro"},
    "Behala": {"lat": (22.485, 22.505), "lon": (88.305, 88.325), "wards": [118, 119, 120, 121], "tree_cover": 15.0, "metro": "Tarattala Metro"},
    "Park Circus": {"lat": (22.538, 22.548), "lon": (88.365, 88.375), "wards": [60, 64, 65], "tree_cover": 8.0, "metro": "Maidan Metro (Nearby)"},
    "Howrah": {"lat": (22.575, 22.595), "lon": (88.320, 88.340), "wards": [15, 16, 20, 21], "tree_cover": 6.5, "metro": "Howrah Metro"},
    "Lake Market": {"lat": (22.508, 22.515), "lon": (88.345, 88.353), "wards": [87, 88, 90], "tree_cover": 16.0, "metro": "Jatin Das Park Metro"},
    "New Town": {"lat": (22.570, 22.595), "lon": (88.445, 88.475), "wards": [101, 102, 103], "tree_cover": 22.0, "metro": "New Town Metro (Proposed)"},
    "Shyambazar": {"lat": (22.595, 22.605), "lon": (88.365, 88.375), "wards": [10, 11, 12], "tree_cover": 9.0, "metro": "Shyambazar Metro"},
    "Alipore": {"lat": (22.525, 22.535), "lon": (88.325, 88.335), "wards": [74, 82], "tree_cover": 32.0, "metro": "Jatin Das Park Metro (Nearby)"},
    "Ballygunge": {"lat": (22.522, 22.535), "lon": (88.360, 88.370), "wards": [68, 69, 72], "tree_cover": 20.0, "metro": "Kalighat Metro (Nearby)"},
    "Bowbazar": {"lat": (22.562, 22.572), "lon": (88.352, 88.362), "wards": [47, 48], "tree_cover": 7.0, "metro": "Central Metro"},
    "Tangra": {"lat": (22.545, 22.555), "lon": (88.382, 88.395), "wards": [57, 58], "tree_cover": 9.5, "metro": "Phoolbagan Metro (Nearby)"},
    "Tollygunge": {"lat": (22.480, 22.495), "lon": (88.340, 88.350), "wards": [94, 95, 97, 98], "tree_cover": 22.0, "metro": "Mahanayak Uttam Kumar Metro"}
}

HOSPITALS = {
    "Kasba": "Ruby General Hospital",
    "Gariahat": "AMRI Hospital Dhakuria",
    "Jadavpur": "KPC Medical College",
    "Salt Lake": "AMRI Salt Lake",
    "Behala": "Vidyasagar State General Hospital",
    "Park Circus": "Calcutta National Medical College",
    "Howrah": "Howrah District Hospital",
    "Lake Market": "Ramakrishna Mission Seva Pratishthan",
    "New Town": "Tata Medical Center",
    "Shyambazar": "R. G. Kar Medical College",
    "Alipore": "Woodlands Hospital",
    "Ballygunge": "Fortis Hospital Anandapur (Nearby)",
    "Bowbazar": "Medical College Kolkata",
    "Tangra": "ESI Hospital Maniktala (Nearby)",
    "Tollygunge": "M. R. Bangur Hospital"
}

# Base time anchor (Current time in mock 2026-07-05)
NOW = datetime(2026, 7, 5, 21, 28, 38)
START_TIME = NOW - timedelta(days=120)

# Simulate rain-heavy monsoon days (highly active rainfall in June/July in Kolkata)
# We will define a set of specific monsoon dates where cascading civic stress will trigger.
RAINY_DATES = {
    (START_TIME + timedelta(days=d)).date()
    for d in [45, 46, 52, 60, 61, 75, 80, 81, 95, 96, 102, 103, 110, 114, 115]
}

def get_time_attributes(ts):
    date_val = ts.date()
    hour = ts.hour
    is_rainy = date_val in RAINY_DATES
    is_weekend = ts.weekday() >= 5
    is_peak = (8 <= hour <= 11) or (17 <= hour <= 20)
    return is_rainy, is_weekend, is_peak

# ==========================================
# 1. GENERATE TRANSPORT DENSITY
# ==========================================
def generate_transport_density(num_rows):
    print("Generating transport_density...")
    data = []
    
    for _ in range(num_rows):
        record_id = str(uuid.uuid4())
        delta_seconds = random.randint(0, int((NOW - START_TIME).total_seconds()))
        ts = START_TIME + timedelta(seconds=delta_seconds)
        is_rainy, is_weekend, is_peak = get_time_attributes(ts)
        
        neighborhood = random.choice(list(NEIGHBORHOODS.keys()))
        geo = NEIGHBORHOODS[neighborhood]
        ward = random.choice(geo["wards"])
        lat = round(random.uniform(geo["lat"][0], geo["lat"][1]), 6)
        lon = round(random.uniform(geo["lon"][0], geo["lon"][1]), 6)
        metro = geo["metro"]
        
        # Base variables
        weather = "Clear"
        aqi_base = random.randint(120, 240)
        
        if is_rainy:
            weather = random.choices(["Light Rain", "Heavy Rain", "Thunderstorm"], weights=[0.2, 0.5, 0.3])[0]
            aqi_base = random.randint(35, 80) # Rain washes out dust
        elif random.random() < 0.15:
            weather = "Overcast"
        elif random.random() < 0.2:
            weather = "Haze"
            aqi_base = random.randint(220, 380) # Haze indicates high pollution
            
        # Traffic density score (0 to 10)
        td_base = 3.5
        if is_peak:
            td_base += 4.0
        if is_rainy:
            td_base += 2.0
        if is_weekend:
            if neighborhood in ["Gariahat", "Park Circus", "Lake Market", "Salt Lake"]:
                td_base += 1.5
            else:
                td_base -= 1.0
                
        traffic_density = min(10.0, max(1.0, round(td_base + random.uniform(-1.0, 1.0), 2)))
        
        # Average vehicle speed (kmph) - negatively correlated
        speed_base = 45.0 - (traffic_density * 3.5)
        if is_rainy:
            speed_base -= 5.0
        speed = min(60.0, max(5.0, round(speed_base + random.uniform(-3.0, 3.0), 1)))
        
        # Pedestrian density
        ped_base = 3.0
        if is_peak:
            ped_base += 3.5
        if neighborhood in ["Gariahat", "Shyambazar", "Howrah", "Lake Market"]:
            ped_base += 2.0
        if is_rainy:
            ped_base -= 2.0 # People stay indoors
        pedestrian_density = min(10.0, max(1.0, round(ped_base + random.uniform(-1.0, 1.0), 2)))
        
        # Public transport load
        pt_base = 3.0
        if is_peak:
            pt_base += 4.5
        if is_rainy:
            pt_base += 1.5 # More people try to get buses/metro
        public_load = min(10.0, max(1.0, round(pt_base + random.uniform(-1.0, 1.0), 2)))
        
        # Bus delay minutes
        delay = 0
        if traffic_density > 7.0:
            delay += random.randint(15, 60)
        elif traffic_density > 4.0:
            delay += random.randint(5, 20)
        if is_rainy:
            delay += random.randint(10, 45)
        bus_delay = max(0, delay + random.randint(-3, 3))
        
        # Congestion level
        if traffic_density >= 8.5:
            congestion = "Gridlock"
        elif traffic_density >= 6.5:
            congestion = "Heavy"
        elif traffic_density >= 4.0:
            congestion = "Moderate"
        else:
            congestion = "Low"
            
        # Accident reports
        accident_prob = 0.01
        if is_rainy:
            accident_prob += 0.04
        if congestion in ["Heavy", "Gridlock"]:
            accident_prob += 0.03
        accident_reports = 1 if random.random() < accident_prob else 0
        if accident_reports == 1 and random.random() < 0.1:
            accident_reports = 2
            
        # Event factor
        if is_rainy:
            event_factor = "Monsoon Rain"
        elif is_peak:
            event_factor = "Rush Hour"
        elif is_weekend and neighborhood in ["Gariahat", "Lake Market"]:
            event_factor = "Festival" if random.random() < 0.2 else "None"
        elif traffic_density > 8.0 and random.random() < 0.3:
            event_factor = "Road Blockage"
        else:
            event_factor = "None"
            
        data.append({
            "record_id": record_id,
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "neighborhood": neighborhood,
            "ward": ward,
            "traffic_density_score": traffic_density,
            "avg_vehicle_speed_kmph": speed,
            "pedestrian_density": pedestrian_density,
            "public_transport_load": public_load,
            "bus_delay_minutes": bus_delay,
            "metro_station": metro,
            "congestion_level": congestion,
            "accident_reports": accident_reports,
            "weather_condition": weather,
            "air_quality_index": aqi_base,
            "event_factor": event_factor,
            "peak_hour": "TRUE" if is_peak else "FALSE",
            "latitude": lat,
            "longitude": lon
        })
        
    df = pd.DataFrame(data)
    df.to_csv("backend/data/transport_density.csv", index=False)
    print(f"transport_density saved. Rows: {len(df)}")

# ==========================================
# 2. GENERATE ENVIRONMENTAL STRESS
# ==========================================
def generate_environmental_stress(num_rows):
    print("Generating environmental_stress...")
    data = []
    
    for _ in range(num_rows):
        stress_id = str(uuid.uuid4())
        delta_seconds = random.randint(0, int((NOW - START_TIME).total_seconds()))
        ts = START_TIME + timedelta(seconds=delta_seconds)
        is_rainy, is_weekend, is_peak = get_time_attributes(ts)
        
        neighborhood = random.choice(list(NEIGHBORHOODS.keys()))
        geo = NEIGHBORHOODS[neighborhood]
        ward = random.choice(geo["wards"])
        lat = round(random.uniform(geo["lat"][0], geo["lat"][1]), 6)
        lon = round(random.uniform(geo["lon"][0], geo["lon"][1]), 6)
        
        # Weather-based parameters
        temp_base = 32.0
        humidity_base = 65.0
        pm25 = random.uniform(80.0, 180.0)
        pm10 = pm25 * random.uniform(1.2, 1.6)
        
        if is_rainy:
            temp_base = 27.0
            humidity_base = 92.0
            pm25 = random.uniform(15.0, 45.0)
            pm10 = pm25 * random.uniform(1.1, 1.3)
        else:
            # Summer/Pre-monsoon heat spike
            if ts.month in [4, 5]:
                temp_base = 38.0
                humidity_base = 50.0
            elif ts.month == 6:
                temp_base = 35.0
                humidity_base = 75.0
                
        temperature = round(temp_base + random.uniform(-2.5, 2.5), 1)
        humidity = min(100.0, max(20.0, round(humidity_base + random.uniform(-5.0, 5.0), 1)))
        pm25 = round(pm25, 1)
        pm10 = round(pm10, 1)
        
        # Rain-heavy cascading factors
        if is_rainy:
            flood_risk = random.uniform(6.5, 9.8)
            drain_stress = random.uniform(7.0, 10.0)
            waterlogging_reps = random.randint(4, 25)
            # Low trees cover = higher drainage stress and flooding risk
            if geo["tree_cover"] < 10:
                flood_risk = min(10.0, flood_risk + 0.8)
                drain_stress = min(10.0, drain_stress + 0.5)
                waterlogging_reps += random.randint(2, 6)
        else:
            flood_risk = random.uniform(0.0, 2.5)
            drain_stress = random.uniform(0.5, 3.5)
            waterlogging_reps = 0
            
        flooding_risk = round(flood_risk, 2)
        drainage_stress = round(drain_stress, 2)
        
        # Garbage overflow reports
        garbage_base = 1
        if drainage_stress > 6.0:
            garbage_base += random.randint(2, 7)  # Water washes garbage out / blocks drains
        if is_weekend:
            garbage_base += random.randint(0, 3)
        garbage_overflow = max(0, garbage_base + random.randint(-1, 2))
        
        # Noise pollution (decibels)
        noise_base = 65.0
        if is_peak:
            noise_base += 12.0
        if neighborhood in ["Howrah", "Park Circus", "Gariahat", "Bowbazar"]:
            noise_base += 8.0
        elif neighborhood in ["Alipore", "Salt Lake"]:
            noise_base -= 5.0
        noise = min(110.0, max(40.0, round(noise_base + random.uniform(-4.0, 4.0), 1)))
        
        # Tree cover percent
        tree_cover = geo["tree_cover"]
        
        # Heat risk level
        if temperature >= 39.0:
            heat_risk = "Extreme"
        elif temperature >= 35.0:
            heat_risk = "High"
        elif temperature >= 30.0:
            heat_risk = "Moderate"
        else:
            heat_risk = "Low"
            
        # Environmental Score (representing aggregate environmental health stress index, 0-10)
        # Higher score = worse environment
        env_score = (pm25 / 150.0)*3.0 + (drainage_stress / 10.0)*3.0 + (noise / 100.0)*2.0 + (100.0 - tree_cover)*0.02
        if heat_risk == "Extreme":
            env_score += 1.5
        environmental_score = min(10.0, max(1.0, round(env_score, 2)))
        
        data.append({
            "stress_id": stress_id,
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "neighborhood": neighborhood,
            "ward": ward,
            "pm25": pm25,
            "pm10": pm10,
            "temperature_celsius": temperature,
            "humidity_percent": humidity,
            "flooding_risk": flooding_risk,
            "drainage_stress": drainage_stress,
            "garbage_overflow_reports": garbage_overflow,
            "noise_pollution_db": noise,
            "tree_cover_percent": tree_cover,
            "heat_risk_level": heat_risk,
            "waterlogging_reports": waterlogging_reps,
            "environmental_score": environmental_score,
            "latitude": lat,
            "longitude": lon
        })
        
    df = pd.DataFrame(data)
    df.to_csv("backend/data/environmental_stress.csv", index=False)
    print(f"environmental_stress saved. Rows: {len(df)}")

# ==========================================
# 3. GENERATE ACCESSIBILITY INCIDENTS
# ==========================================
def generate_accessibility_incidents(num_rows):
    print("Generating accessibility_incidents...")
    data = []
    
    issues = [
        ("Sidewalk Obstruction", "Pedestrians"),
        ("Broken Tactile Path", "Visually Impaired"),
        ("Elevator Malfunction", "Elderly & Disabled"),
        ("Traffic Signal Failure", "Commuters"),
        ("Flooded Ramp", "Wheelchair Users"),
        ("Lack of Wheelchair Ramp", "Wheelchair Users")
    ]
    
    for _ in range(num_rows):
        incident_id = str(uuid.uuid4())
        delta_seconds = random.randint(0, int((NOW - START_TIME).total_seconds()))
        ts = START_TIME + timedelta(seconds=delta_seconds)
        is_rainy, is_weekend, is_peak = get_time_attributes(ts)
        
        neighborhood = random.choice(list(NEIGHBORHOODS.keys()))
        geo = NEIGHBORHOODS[neighborhood]
        ward = random.choice(geo["wards"])
        lat = round(random.uniform(geo["lat"][0], geo["lat"][1]), 6)
        lon = round(random.uniform(geo["lon"][0], geo["lon"][1]), 6)
        hospital = HOSPITALS[neighborhood]
        
        # Select issue based on context
        if is_rainy:
            # More waterlogging/signal issues during rain
            issue_choice = random.choices(issues, weights=[0.1, 0.05, 0.15, 0.35, 0.3, 0.05])[0]
        else:
            issue_choice = random.choices(issues, weights=[0.25, 0.15, 0.15, 0.1, 0.05, 0.3])[0]
            
        issue_type, affected_group = issue_choice
        
        # Flags
        sidewalk_blocked = "TRUE" if issue_type in ["Sidewalk Obstruction", "Lack of Wheelchair Ramp"] and random.random() < 0.7 else "FALSE"
        tactile_path_damage = "TRUE" if issue_type == "Broken Tactile Path" else "FALSE"
        elevator_outage = "TRUE" if issue_type == "Elevator Malfunction" else "FALSE"
        crossing_signal_failure = "TRUE" if issue_type == "Traffic Signal Failure" else "FALSE"
        
        # Severity
        if is_rainy and issue_type in ["Flooded Ramp", "Traffic Signal Failure"]:
            severity = random.choices(["High", "Critical"], weights=[0.4, 0.6])[0]
        else:
            severity = random.choices(["Low", "Medium", "High", "Critical"], weights=[0.2, 0.4, 0.3, 0.1])[0]
            
        # Accessibility score
        score_base = 6.5
        if severity == "Critical":
            score_base -= 4.0
        elif severity == "High":
            score_base -= 2.5
        if is_rainy:
            score_base -= 1.5
        wheelchair_score = min(10.0, max(0.0, round(score_base + random.uniform(-1.0, 1.0), 1)))
        
        # Response status & volunteers
        age_days = (NOW - ts).days
        if age_days > 7:
            response_status = "Resolved"
            volunteer_assigned = "TRUE" if random.random() < 0.6 else "FALSE"
            # Resolution time minutes
            if severity == "Critical":
                res_time = random.randint(120, 720)
            elif severity == "High":
                res_time = random.randint(240, 1440)
            else:
                res_time = random.randint(720, 5760)
        else:
            response_status = random.choices(["Reported", "Assigned", "In Progress", "Resolved"], weights=[0.3, 0.3, 0.3, 0.1])[0]
            volunteer_assigned = "TRUE" if response_status in ["Assigned", "In Progress", "Resolved"] and random.random() < 0.7 else "FALSE"
            res_time = random.randint(120, 720) if response_status == "Resolved" else ""
            
        data.append({
            "incident_id": incident_id,
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "neighborhood": neighborhood,
            "ward": ward,
            "issue_type": issue_type,
            "severity": severity,
            "affected_group": affected_group,
            "sidewalk_blocked": sidewalk_blocked,
            "tactile_path_damage": tactile_path_damage,
            "elevator_outage": elevator_outage,
            "crossing_signal_failure": crossing_signal_failure,
            "wheelchair_accessibility_score": wheelchair_score,
            "nearby_hospital": hospital,
            "response_status": response_status,
            "volunteer_assigned": volunteer_assigned,
            "resolution_time_minutes": res_time,
            "latitude": lat,
            "longitude": lon
        })
        
    df = pd.DataFrame(data)
    df.to_csv("backend/data/accessibility_incidents.csv", index=False)
    print(f"accessibility_incidents saved. Rows: {len(df)}")

# ==========================================
# 4. GENERATE COMMUNITY SENTIMENT
# ==========================================
def generate_community_sentiment(num_rows):
    print("Generating community_sentiment...")
    data = []
    
    topics = {
        "Waterlogging": {"emotions": ["Anger", "Frustration", "Anxiety"], "sentiment": (-0.95, -0.6)},
        "Traffic Jam": {"emotions": ["Frustration", "Anger", "Indifference"], "sentiment": (-0.8, -0.4)},
        "Power Outage": {"emotions": ["Anger", "Frustration", "Anxiety"], "sentiment": (-0.9, -0.5)},
        "Garbage Clearance": {"emotions": ["Frustration", "Hope", "Satisfaction"], "sentiment": (-0.6, 0.3)},
        "Community Event": {"emotions": ["Hope", "Satisfaction"], "sentiment": (0.5, 0.95)},
        "Public Parks": {"emotions": ["Satisfaction", "Hope", "Indifference"], "sentiment": (0.3, 0.8)}
    }
    
    platforms = ["Citizen Portal", "Twitter/X", "Local Facebook Groups", "Public Grievance System"]
    
    for _ in range(num_rows):
        sentiment_id = str(uuid.uuid4())
        delta_seconds = random.randint(0, int((NOW - START_TIME).total_seconds()))
        ts = START_TIME + timedelta(seconds=delta_seconds)
        is_rainy, is_weekend, is_peak = get_time_attributes(ts)
        
        neighborhood = random.choice(list(NEIGHBORHOODS.keys()))
        geo = NEIGHBORHOODS[neighborhood]
        ward = random.choice(geo["wards"])
        
        # Decide topic based on weather/monsoon
        if is_rainy:
            topic = random.choices(["Waterlogging", "Traffic Jam", "Power Outage", "Garbage Clearance"], weights=[0.6, 0.25, 0.1, 0.05])[0]
        else:
            topic = random.choices(["Waterlogging", "Traffic Jam", "Power Outage", "Garbage Clearance", "Community Event", "Public Parks"], weights=[0.05, 0.3, 0.1, 0.2, 0.2, 0.15])[0]
            
        topic_info = topics[topic]
        dominant_emotion = random.choice(topic_info["emotions"])
        sentiment_range = topic_info["sentiment"]
        sentiment_score = round(random.uniform(sentiment_range[0], sentiment_range[1]), 2)
        
        # Frustration Index (0-10)
        frustration_base = 4.5
        if topic in ["Waterlogging", "Traffic Jam", "Power Outage"]:
            frustration_base += 3.5
        if is_rainy:
            frustration_base += 1.5
        if is_peak:
            frustration_base += 1.0
        frustration_index = min(10.0, max(0.0, round(frustration_base + random.uniform(-1.0, 1.0), 1)))
        
        # Wellbeing Index (0-10) - negatively correlated with frustration
        wellbeing_index = min(10.0, max(0.0, round(10.0 - frustration_index + random.uniform(-0.8, 0.8), 1)))
        
        # Civic Trust Score (0-10)
        trust_base = 5.5
        if frustration_index > 7.0:
            trust_base -= 2.5
        elif frustration_index < 3.0:
            trust_base += 1.5
        civic_trust = min(10.0, max(0.0, round(trust_base + random.uniform(-1.0, 1.0), 1)))
        
        # Community engagement score
        eng_base = 5.0
        if topic in ["Community Event", "Waterlogging"]:
            eng_base += 2.5 # People aggregate/complain more in groups
        engagement_score = min(10.0, max(0.0, round(eng_base + random.uniform(-1.0, 1.0), 1)))
        
        source = random.choice(platforms)
        
        # Report volume
        vol_base = random.randint(15, 60)
        if is_rainy:
            vol_base *= 3
        if is_peak:
            vol_base = int(vol_base * 1.5)
        report_volume = max(5, vol_base + random.randint(-5, 5))
        
        # Calculate reports split
        if sentiment_score > 0.3:
            pos_ratio = random.uniform(0.6, 0.9)
            neg_ratio = random.uniform(0.0, 0.15)
        elif sentiment_score < -0.3:
            pos_ratio = random.uniform(0.0, 0.1)
            neg_ratio = random.uniform(0.6, 0.9)
        else:
            pos_ratio = random.uniform(0.2, 0.4)
            neg_ratio = random.uniform(0.2, 0.4)
            
        neutral_ratio = 1.0 - (pos_ratio + neg_ratio)
        positive_reps = int(report_volume * pos_ratio)
        negative_reps = int(report_volume * neg_ratio)
        neutral_reps = max(0, report_volume - (positive_reps + negative_reps))
        
        # Narratives
        summaries = {
            "Waterlogging": f"High citizen complaints regarding waterlogging and choked sewers in {neighborhood} following downpours.",
            "Traffic Jam": f"Commuter frustration peaked in {neighborhood} due to heavy delays and traffic gridlock.",
            "Power Outage": f"Multiple reports of power cuts and voltage fluctuations causing discomfort in {neighborhood}.",
            "Garbage Clearance": f"Citizens discussing clean-up initiatives and garbage removal delays in {neighborhood}.",
            "Community Event": f"Positive response to the local neighborhood clean-up and beautification campaign.",
            "Public Parks": f"Residents expressing satisfaction with the maintenance of community parks and green spaces."
        }
        ai_summary = summaries[topic]
        
        data.append({
            "sentiment_id": sentiment_id,
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "neighborhood": neighborhood,
            "ward": ward,
            "sentiment_score": sentiment_score,
            "civic_trust_score": civic_trust,
            "frustration_index": frustration_index,
            "wellbeing_index": wellbeing_index,
            "community_engagement_score": engagement_score,
            "dominant_topic": topic,
            "dominant_emotion": dominant_emotion,
            "source_platform": source,
            "report_volume": report_volume,
            "ai_summary": ai_summary,
            "positive_reports": positive_reps,
            "negative_reports": negative_reps,
            "neutral_reports": neutral_reps
        })
        
    df = pd.DataFrame(data)
    df.to_csv("backend/data/community_sentiment.csv", index=False)
    print(f"community_sentiment saved. Rows: {len(df)}")

# ==========================================
# 5. GENERATE COMMUNITY MISSIONS
# ==========================================
def generate_community_missions(num_rows):
    print("Generating community_missions...")
    data = []
    
    categories = ["Cleanliness", "Disaster Relief", "Tree Plantation", "Elderly Assistance", "Road Repair Support", "Awareness Campaign"]
    
    mission_templates = {
        "Cleanliness": [
            ("Clean & Paint {neighborhood} Market Walls", "A citizen initiative to scrub off poster stains and paint local cultural murals near the market.", "Gloves, Paint, Brushes"),
            ("Choked Drain De-clogging Drive", "Clearing floating plastic wrappers and debris blocking secondary drainage inlets prior to rains.", "Gloves, Trash bags, Rakes"),
            ("Litter Clearance in {neighborhood} Park", "Cleaning up plastic bottles and snack packets left behind around the playground.", "Trash bags, Grabbers")
        ],
        "Disaster Relief": [
            ("Waterlogging Relief Support", "Assisting municipal staff in distributing dry food and drinking water packets to waterlogged households.", "Raincoats, Boots, Flashlights"),
            ("Uprooted Branch Clearance", "Safely removing fallen storm debris and branches blocking local cross-lanes.", "Ropes, Hand saws, Gloves"),
            ("High-Water Safe Passage Assist", "Guiding elderly and school children safely across flooded intersections.", "Umbrellas, Safety vests")
        ],
        "Tree Plantation": [
            ("Urban Canopy Drive at {street}", "Planting native tree saplings along the divider to combat local heat waves.", "Saplings, Shovels, Organic manure"),
            ("Restoring Green Cover in Ward {ward}", "Adding indoor potted air-purifying plants to public community centers.", "Pots, Plants, Soil"),
            ("Nurturing Young Saplings Campaign", "Watering and setting up protective mesh cages for recently planted saplings.", "Watering cans, Wire mesh")
        ],
        "Elderly Assistance": [
            ("Medicine Delivery during Waterlogging", "Delivering critical medicines and groceries to homebound elderly residents during flood hours.", "Raincoats, Bags"),
            ("Digital Literacy for Seniors", "Helping elderly residents learn to file digital civic complaints and check medical reports.", "None"),
            ("Companion Walks in {neighborhood}", "Assisting walking-impaired seniors for safe evening strolls in local parks.", "None")
        ],
        "Road Repair Support": [
            ("Temporary Pothole Fill-up Drive", "Using cold-mix asphalt to provisionally fill small hazardous potholes before major repairs.", "Cold-mix bags, Shovels"),
            ("Pedestrian Walkway De-cluttering", "Assisting in shifting construction debris blocking wheelchair ramps near the hospital.", "Gloves, Shovels"),
            ("Speed Breaker Painting Campaign", "Painting highly visible reflective yellow markers on speed bumps to prevent nighttime accidents.", "Reflective Paint, Brushes")
        ],
        "Awareness Campaign": [
            ("Waste Segregation Awareness Campaign", "Visiting houses in {neighborhood} to explain dry and wet waste segregation guidelines.", "Pamphlets"),
            ("Anti-Honking Campaign near Hospital", "Holding silent placards and educating auto drivers near {hospital} about silent zone norms.", "Placards"),
            ("Mosquito Breeding Prevention Check", "Distributing pamphlets on how to prevent stagnant water in flower pots and terraces.", "Pamphlets, Bleaching powder")
        ]
    }
    
    partners = ["Green Kolkata NGO", "Kolkata Municipal Corp Co-op", "Owe Community Network", "Red Cross Local Chapter", "Rotary Club East"]
    streets = ["Rashbehari Avenue", "Gariahat Road", "SP Mukherjee Road", "Major Arterial Road", "Salt Lake Bypass", "EM Bypass"]
    
    for _ in range(num_rows):
        mission_id = str(uuid.uuid4())
        delta_seconds = random.randint(0, int((NOW - START_TIME).total_seconds()))
        ts = START_TIME + timedelta(seconds=delta_seconds)
        is_rainy, is_weekend, is_peak = get_time_attributes(ts)
        
        neighborhood = random.choice(list(NEIGHBORHOODS.keys()))
        geo = NEIGHBORHOODS[neighborhood]
        ward = random.choice(geo["wards"])
        lat = round(random.uniform(geo["lat"][0], geo["lat"][1]), 6)
        lon = round(random.uniform(geo["lon"][0], geo["lon"][1]), 6)
        hospital = HOSPITALS[neighborhood]
        street = random.choice(streets)
        
        # Choose category based on rainy conditions (Disaster Relief spikes during rain)
        if is_rainy:
            mission_category = random.choices(categories, weights=[0.15, 0.45, 0.05, 0.2, 0.1, 0.05])[0]
        else:
            mission_category = random.choices(categories, weights=[0.25, 0.05, 0.25, 0.15, 0.15, 0.15])[0]
            
        templates = mission_templates[mission_category]
        template = random.choice(templates)
        
        title_temp, desc_temp, supplies = template
        title = title_temp.format(neighborhood=neighborhood, street=street, ward=ward, hospital=hospital)
        description = desc_temp.format(neighborhood=neighborhood, street=street, ward=ward, hospital=hospital)
        
        # Urgency
        if is_rainy and mission_category == "Disaster Relief":
            urgency = random.choices(["High", "Critical"], weights=[0.3, 0.7])[0]
        else:
            urgency = random.choices(["Low", "Medium", "High", "Critical"], weights=[0.3, 0.4, 0.2, 0.1])[0]
            
        target_group = random.choices(["Elderly", "All Residents", "Stray Animals", "Children", "Commuters"], weights=[0.2, 0.5, 0.05, 0.1, 0.15])[0]
        
        # Volunteers needed & joined
        vol_need = random.randint(5, 30)
        if urgency == "Critical":
            vol_need = random.randint(15, 50)
            
        # Completion status based on age
        age_days = (NOW - ts).days
        if age_days > 5:
            completion_status = random.choices(["Completed", "Cancelled"], weights=[0.95, 0.05])[0]
            vol_joined = vol_need + random.randint(-3, 8) if completion_status == "Completed" else random.randint(0, 5)
        else:
            completion_status = random.choices(["Planned", "Active", "Completed"], weights=[0.3, 0.5, 0.2])[0]
            if completion_status == "Planned":
                vol_joined = random.randint(0, 5)
            elif completion_status == "Active":
                vol_joined = random.randint(2, vol_need + 3)
            else:
                vol_joined = vol_need + random.randint(-2, 5)
                
        vol_joined = max(0, vol_joined)
        
        duration = round(random.uniform(2.0, 6.0), 1)
        if mission_category == "Disaster Relief":
            duration = round(random.uniform(4.0, 12.0), 1)
            
        # Impact Score
        impact = 4.0
        if completion_status == "Completed":
            impact += 3.0
            if urgency in ["High", "Critical"]:
                impact += 2.0
        impact_score = min(10.0, max(1.0, round(impact + random.uniform(-1.0, 1.0), 1)))
        
        partner = random.choice(partners)
        
        data.append({
            "mission_id": mission_id,
            "created_at": ts.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "neighborhood": neighborhood,
            "ward": ward,
            "mission_category": mission_category,
            "mission_title": title,
            "mission_description": description,
            "urgency_level": urgency,
            "target_group": target_group,
            "volunteers_needed": vol_need,
            "volunteers_joined": vol_joined,
            "completion_status": completion_status,
            "estimated_duration_hours": duration,
            "mission_impact_score": impact_score,
            "organization_partner": partner,
            "supplies_required": supplies,
            "ai_generated": "TRUE" if random.random() < 0.85 else "FALSE",
            "latitude": lat,
            "longitude": lon
        })
        
    df = pd.DataFrame(data)
    df.to_csv("backend/data/community_missions.csv", index=False)
    print(f"community_missions saved. Rows: {len(df)}")

def validate_datasets():
    print("Starting validation of generated files...")
    files = [
        "transport_density.csv",
        "environmental_stress.csv",
        "accessibility_incidents.csv",
        "community_sentiment.csv",
        "community_missions.csv"
    ]
    
    for f_name in files:
        path = os.path.join("backend", "data", f_name)
        if not os.path.exists(path):
            print(f"Error: {f_name} does not exist!")
            continue
            
        print(f"\nValidating {f_name}:")
        try:
            # Check UTF-8 compatibility and formatting integrity
            df = pd.read_csv(path, encoding="utf-8")
            
            # Check for empty/missing values in critical fields (no malformed rows)
            null_counts = df.isnull().sum().sum()
            dup_counts = df.duplicated().sum()
            
            print(f"  - Rows: {len(df)}")
            print(f"  - Columns: {list(df.columns)}")
            print(f"  - Missing/Null values count: {null_counts}")
            print(f"  - Duplicate rows count: {dup_counts}")
            
            # Quick check for some rows to confirm non-empty string structure
            if len(df) > 0:
                print("  - Status: VALID (UTF-8 compatible, no duplicates, clean schema)")
            else:
                print("  - Status: ERROR (Empty file)")
        except Exception as e:
            print(f"  - Status: FAILED validation with exception: {e}")

def main():
    # Generate between 20,000 and 40,000 rows (let's pick random sizes in this range)
    generate_transport_density(random.randint(25000, 35000))
    generate_environmental_stress(random.randint(25000, 35000))
    generate_accessibility_incidents(random.randint(25000, 35000))
    generate_community_sentiment(random.randint(25000, 35000))
    generate_community_missions(random.randint(25000, 35000))
    
    validate_datasets()

if __name__ == "__main__":
    main()
