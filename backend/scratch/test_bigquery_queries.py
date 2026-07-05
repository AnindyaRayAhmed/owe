import os
import sys

# Ensure backend folder is in path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from services.bigquery_service import BigQueryService

def test_queries():
    print("Initializing BigQueryService...")
    service = BigQueryService()
    
    print("\n1. Testing get_dashboard_metrics...")
    try:
        metrics = service.get_dashboard_metrics()
        print("  Success! Dashboard metrics keys:", list(metrics.keys()))
    except Exception as e:
        print("  Failed:", e)
        
    print("\n2. Testing get_emerging_signals...")
    try:
        signals = service.get_emerging_signals()
        print("  Success! Number of emerging signals:", len(signals))
    except Exception as e:
        print("  Failed:", e)
        
    print("\n3. Testing get_community_momentum...")
    try:
        momentum = service.get_community_momentum()
        print("  Success! Number of momentum records:", len(momentum))
    except Exception as e:
        print("  Failed:", e)
        
    print("\n4. Testing get_active_missions...")
    try:
        missions = service.get_active_missions()
        print("  Success! Number of active missions:", len(missions))
    except Exception as e:
        print("  Failed:", e)
        
    print("\n5. Testing get_transport_density...")
    try:
        td = service.get_transport_density()
        print("  Success! Number of transport density records:", len(td))
    except Exception as e:
        print("  Failed:", e)
        
    print("\n6. Testing get_environmental_stress...")
    try:
        es = service.get_environmental_stress()
        print("  Success! Number of environmental stress records:", len(es))
    except Exception as e:
        print("  Failed:", e)
        
    print("\n7. Testing get_accessibility_summary...")
    try:
        acc = service.get_accessibility_summary()
        print("  Success! Number of accessibility records:", len(acc))
    except Exception as e:
        print("  Failed:", e)
        
    print("\n8. Testing get_sentiment_summary...")
    try:
        sent = service.get_sentiment_summary()
        print("  Success! Number of sentiment summary records:", len(sent))
    except Exception as e:
        print("  Failed:", e)
        
    print("\n9. Testing get_debug_info...")
    try:
        debug_info = service.get_debug_info()
        print("  Success! Debug Info status:", debug_info.get("status"))
    except Exception as e:
        print("  Failed:", e)

if __name__ == "__main__":
    test_queries()
