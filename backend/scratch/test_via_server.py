import os
import sys
import subprocess
import time
import urllib.request
import urllib.parse
import json

def test_via_server():
    backend_dir = os.path.join(os.path.dirname(__file__), "..")
    
    print("Launching Uvicorn server...")
    # Start uvicorn in the background using python -m uvicorn
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--port", "8089", "--host", "127.0.0.1"],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(3)
    
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
    finally:
        print("Terminating Uvicorn server...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
            
    if success:
        print("ALL TESTS PASSED SUCCESSFUL!")
        sys.exit(0)
    else:
        print("TESTS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    test_via_server()
