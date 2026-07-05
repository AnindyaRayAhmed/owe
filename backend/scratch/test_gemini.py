import os
import sys

# Ensure backend folder is in path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from services.gemini_client import GeminiClient

def test_client():
    print("Initializing GeminiClient...")
    client = GeminiClient()
    status = client.get_debug_status()
    print("Debug status:", status)
    
    if status["mode"] == "simulation":
        print("Running in simulation mode (No API Key set). Refactoring works for local dev fallback.")
    else:
        print("Running in live Gemini mode! Testing JSON generation...")
        try:
            prompt = "Return a JSON object listing the top 3 neighborhoods in Kolkata. Format: {'neighborhoods': ['name1', 'name2', 'name3']}"
            result = client.generate_json_content(prompt)
            print("Result:", result)
            assert "neighborhoods" in result, "Result key missing!"
            print("Test SUCCESSFUL!")
        except Exception as e:
            print("Test FAILED:", e)

if __name__ == "__main__":
    test_client()
