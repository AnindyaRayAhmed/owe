import urllib.request
import urllib.parse
import json
import sys

def check_live_endpoints():
    base_url = "http://127.0.0.1:8089"
    success = True
    
    try:
        # 1. Health check
        print("Testing health check...")
        res = urllib.request.urlopen(f"{base_url}/api/health")
        data = json.loads(res.read().decode())
        print(f"  Health Status: {res.status}, Response: {data}")
        
        # 2. BigQuery debug check
        print("Testing BQ debug check...")
        res = urllib.request.urlopen(f"{base_url}/api/debug/bigquery")
        data = json.loads(res.read().decode())
        print(f"  BQ Debug Status: {res.status}, Response: {data}")
        
        # 3. Daily brief check
        print("Testing daily brief check...")
        res = urllib.request.urlopen(f"{base_url}/api/brief")
        data = json.loads(res.read().decode())
        print(f"  Daily Brief Status: {res.status}, Source: {data.get('source')}")
        
        # 4. Missions check
        print("Testing missions check...")
        res = urllib.request.urlopen(f"{base_url}/api/missions")
        data = json.loads(res.read().decode())
        print(f"  Missions Status: {res.status}, Count: {len(data) if isinstance(data, list) else 'non-list'}")
        
        # 5. Chat check
        print("Testing chat check...")
        payload = json.dumps({"message": "Tell me about traffic density in Kolkata"}).encode("utf-8")
        req = urllib.request.Request(
            f"{base_url}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        res = urllib.request.urlopen(req)
        data = json.loads(res.read().decode())
        print(f"  Chat Status: {res.status}, Reply: {data.get('reply')[:100]}...")
        
    except Exception as e:
        print("Test failed with exception:", e)
        success = False
            
    if success:
        print("\nALL RUNNING ENDPOINTS RETURNED HTTP 200 SUCCESS!")
        sys.exit(0)
    else:
        print("\nSOME ENDPOINTS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    check_live_endpoints()
