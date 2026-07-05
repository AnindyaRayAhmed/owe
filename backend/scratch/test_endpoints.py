import os
import sys

# Ensure backend folder is in path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from main import app

def test_endpoints():
    client = TestClient(app)
    
    print("Testing GET /api/health...")
    r = client.get("/api/health")
    print(f"Status Code: {r.status_code}, Response: {r.json()}")
    assert r.status_code == 200, "Health check failed"

    print("\nTesting GET /api/debug/bigquery...")
    r = client.get("/api/debug/bigquery")
    print(f"Status Code: {r.status_code}, Response: {r.json()}")
    assert r.status_code == 200, "BigQuery debug failed"
    
    print("\nTesting GET /api/brief...")
    r = client.get("/api/brief")
    print(f"Status Code: {r.status_code}, Source: {r.json().get('source') if isinstance(r.json(), dict) else 'none'}")
    assert r.status_code == 200, "Brief endpoint failed"
    
    print("\nTesting GET /api/missions...")
    r = client.get("/api/missions")
    print(f"Status Code: {r.status_code}, Number of missions: {len(r.json()) if isinstance(r.json(), list) else 'none'}")
    assert r.status_code == 200, "Missions endpoint failed"
    
    print("\nTesting POST /api/chat...")
    r = client.post("/api/chat", json={"message": "Explain what's happening with accessibility in Kolkata"})
    print(f"Status Code: {r.status_code}, Response JSON: {r.json()}")
    assert r.status_code == 200, "Chat endpoint failed"
    
    print("\nALL ENDPOINTS RETURNED HTTP 200 SUCCESS!")

if __name__ == "__main__":
    test_endpoints()
