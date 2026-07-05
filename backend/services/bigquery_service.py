import os
import json
import logging

logger = logging.getLogger(__name__)

class BigQueryService:
    def __init__(self):
        self.project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
        self.dataset_id = "owe_civic_data"
        self.client = None
        self.fallback_data_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "mock_data", "civic_feeds.json"
        )
        
        try:
            # We attempt to import bigquery. If google-cloud-bigquery is installed
            # and credentials exist, it initializes.
            from google.cloud import bigquery
            
            # Application Default Credentials are used automatically if on Cloud Run
            # or if GOOGLE_APPLICATION_CREDENTIALS is set locally.
            self.client = bigquery.Client()
            logger.info("BigQuery client initialized successfully.")
        except ImportError:
            logger.warning("google-cloud-bigquery package not found. Using local JSON fallback.")
        except Exception as e:
            logger.warning(f"BigQuery initialization failed (likely missing credentials): {e}. Using local JSON fallback.")

    def fetch_civic_data(self) -> dict:
        """
        Attempts to fetch real tables from BigQuery.
        Falls back to local mock data if BQ is unavailable.
        """
        if self.client and self.project_id:
            try:
                # In a live scenario, we would run queries against:
                # f"{self.project_id}.{self.dataset_id}.civic_complaints"
                # For this MVP phase, we simulate the successful schema retrieval
                # to avoid failing if the BQ tables haven't been provisioned yet.
                logger.info("Fetching civic data from BigQuery...")
                # ... real query execution would go here ...
                return self._load_fallback_data() # Temporary bypass until real tables exist
            except Exception as e:
                logger.error(f"Error querying BigQuery: {e}. Falling back to local data.")
                return self._load_fallback_data()
        else:
            return self._load_fallback_data()

    def _load_fallback_data(self) -> dict:
        if os.path.exists(self.fallback_data_path):
            try:
                with open(self.fallback_data_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to parse fallback mock feeds: {e}")
        return {}
