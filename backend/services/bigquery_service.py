import os
import json
import logging
import time
import concurrent.futures

logger = logging.getLogger(__name__)

class BigQueryService:
    def __init__(self):
        self.project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "default_project")
        self.dataset_id = "owe_civic_data"
        self.client = None
        self.fallback_data_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "mock_data", "civic_feeds.json"
        )
        self._cache = None
        self._cache_time = 0
        
        try:
            from google.cloud import bigquery
            self.client = bigquery.Client()
            if self.client.project:
                self.project_id = self.client.project
            logger.info(f"BigQuery client initialized successfully for project: {self.project_id}")
        except ImportError:
            logger.warning("google-cloud-bigquery package not found. Using local JSON fallback.")
        except Exception as e:
            logger.warning(f"BigQuery initialization failed: {e}. Using local JSON fallback.")

    def _execute_query(self, query: str):
        """Helper to execute BQ query with logging."""
        if not self.client:
            raise Exception("BigQuery client not initialized.")
            
        logger.info(f"Executing SQL Query:\n{query}")
        start_time = time.time()
        try:
            query_job = self.client.query(query)
            results = query_job.result()
            rows = [dict(row) for row in results]
            
            latency = time.time() - start_time
            logger.info(f"BIGQUERY QUERY EXECUTED. ROW COUNTS: {len(rows)}. QUERY LATENCY: {latency:.3f}s")
            return rows
        except Exception as e:
            logger.error(f"Error querying BigQuery: {e}")
            raise e

    def get_dashboard_metrics(self) -> dict:
        if not self.client:
            return self._load_fallback_data()
            
        try:
            query = f"""
                SELECT 
                  (SELECT COUNT(*) FROM `{self.project_id}.{self.dataset_id}.accessibility_incidents` WHERE response_status != 'Resolved' AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)) as friction_points,
                  (SELECT COUNT(*) FROM `{self.project_id}.{self.dataset_id}.community_missions` WHERE completion_status IN ('Active', 'Planned')) as open_missions
            """
            result = self._execute_query(query)
            if result:
                friction = result[0].get("friction_points", 0)
                missions = result[0].get("open_missions", 0)
                pulse_score = max(50, 100 - int(friction * 0.1)) 
                
                return {
                    "friction_points": friction,
                    "open_missions": missions,
                    "pulse_score": pulse_score,
                    "active_neighbors": "2,450"
                }
            return {}
        except Exception as e:
            logger.error(f"Failed to fetch dashboard metrics from BQ: {e}")
            return self._load_fallback_data()

    def get_emerging_signals(self) -> list:
        if not self.client:
            return []
            
        try:
            query = f"""
                SELECT * FROM (
                  SELECT 'Environmental' as type, neighborhood, heat_risk_level as detail, CAST(timestamp AS STRING) as timestamp 
                  FROM `{self.project_id}.{self.dataset_id}.environmental_stress`
                  WHERE (heat_risk_level = 'Extreme' OR flooding_risk > 8.0) AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 48 HOUR)
                  ORDER BY timestamp DESC LIMIT 3
                )
                UNION ALL
                SELECT * FROM (
                  SELECT 'Transport' as type, neighborhood, congestion_level as detail, CAST(timestamp AS STRING) as timestamp
                  FROM `{self.project_id}.{self.dataset_id}.transport_density`
                  WHERE congestion_level = 'Gridlock' AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 48 HOUR)
                  ORDER BY timestamp DESC LIMIT 3
                )
            """
            return self._execute_query(query)
        except Exception as e:
            logger.error(f"Failed to fetch emerging signals: {e}")
            return []

    def get_community_momentum(self) -> list:
        if not self.client:
            return self._load_fallback_data().get("momentum", [])
            
        try:
            query = f"""
                SELECT * FROM (
                  SELECT 'Mission' as type, neighborhood, mission_title as detail, CAST(created_at AS STRING) as timestamp
                  FROM `{self.project_id}.{self.dataset_id}.community_missions`
                  WHERE completion_status = 'Completed' AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
                  ORDER BY created_at DESC LIMIT 3
                )
                UNION ALL
                SELECT * FROM (
                  SELECT 'Sentiment' as type, neighborhood, dominant_topic as detail, CAST(timestamp AS STRING) as timestamp
                  FROM `{self.project_id}.{self.dataset_id}.community_sentiment`
                  WHERE sentiment_score > 0.5 AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
                  ORDER BY timestamp DESC LIMIT 3
                )
            """
            return self._execute_query(query)
        except Exception as e:
            logger.error(f"Failed to fetch community momentum: {e}")
            return self._load_fallback_data().get("momentum", [])

    def get_active_missions(self) -> list:
        if not self.client:
            return self._load_fallback_data().get("missions", [])
            
        try:
            query = f"""
                SELECT * 
                FROM `{self.project_id}.{self.dataset_id}.community_missions`
                WHERE completion_status IN ('Active', 'Planned')
                ORDER BY urgency_level DESC, created_at DESC
                LIMIT 5
            """
            return self._execute_query(query)
        except Exception as e:
            logger.error(f"Failed to fetch active missions: {e}")
            return self._load_fallback_data().get("missions", [])

    def get_transport_density(self) -> list:
        if not self.client:
            return []
        try:
            query = f"""
                SELECT neighborhood, AVG(traffic_density_score) as avg_density, AVG(bus_delay_minutes) as avg_delay
                FROM `{self.project_id}.{self.dataset_id}.transport_density`
                WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 48 HOUR)
                GROUP BY neighborhood
                ORDER BY avg_density DESC
                LIMIT 3
            """
            return self._execute_query(query)
        except Exception as e:
            logger.error(f"Failed to fetch transport density: {e}")
            return []

    def get_environmental_stress(self) -> list:
        if not self.client:
            return []
        try:
            query = f"""
                SELECT neighborhood, AVG(environmental_score) as avg_env_score, AVG(flooding_risk) as avg_flood_risk
                FROM `{self.project_id}.{self.dataset_id}.environmental_stress`
                WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 48 HOUR)
                GROUP BY neighborhood
                ORDER BY avg_env_score DESC
                LIMIT 3
            """
            return self._execute_query(query)
        except Exception as e:
            logger.error(f"Failed to fetch environmental stress: {e}")
            return []

    def get_accessibility_summary(self) -> list:
        if not self.client:
            return []
        try:
            query = f"""
                SELECT neighborhood, issue_type, severity, COUNT(*) as issue_count
                FROM `{self.project_id}.{self.dataset_id}.accessibility_incidents`
                WHERE response_status != 'Resolved' AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
                GROUP BY neighborhood, issue_type, severity
                ORDER BY issue_count DESC
                LIMIT 5
            """
            return self._execute_query(query)
        except Exception as e:
            logger.error(f"Failed to fetch accessibility summary: {e}")
            return []
            
    def get_sentiment_summary(self) -> list:
        if not self.client:
            return []
        try:
            query = f"""
                SELECT neighborhood, AVG(sentiment_score) as avg_sentiment, AVG(frustration_index) as avg_frustration
                FROM `{self.project_id}.{self.dataset_id}.community_sentiment`
                WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 48 HOUR)
                GROUP BY neighborhood
                ORDER BY avg_frustration DESC
                LIMIT 3
            """
            return self._execute_query(query)
        except Exception as e:
            logger.error(f"Failed to fetch sentiment summary: {e}")
            return []

    def fetch_civic_data(self) -> dict:
        """Fetch all data in parallel and cache the result."""
        if not self.client:
            return self._load_fallback_data()
            
        current_time = time.time()
        if self._cache and (current_time - self._cache_time) < 60:
            logger.info("Serving BigQuery data from in-memory cache (TTL: 60s)")
            return self._cache
            
        logger.info("Fetching BigQuery aggregations in parallel...")
        start_time = time.time()
        
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                future_dash = executor.submit(self.get_dashboard_metrics)
                future_signals = executor.submit(self.get_emerging_signals)
                future_momentum = executor.submit(self.get_community_momentum)
                future_missions = executor.submit(self.get_active_missions)
                future_transport = executor.submit(self.get_transport_density)
                future_env = executor.submit(self.get_environmental_stress)
                future_acc = executor.submit(self.get_accessibility_summary)
                future_sent = executor.submit(self.get_sentiment_summary)
                
                result = {
                    "dashboard": future_dash.result(),
                    "emerging_signals": future_signals.result(),
                    "momentum": future_momentum.result(),
                    "missions": future_missions.result(),
                    "transport": future_transport.result(),
                    "environmental": future_env.result(),
                    "accessibility": future_acc.result(),
                    "sentiment": future_sent.result()
                }
                
            self._cache = result
            self._cache_time = current_time
            
            elapsed = time.time() - start_time
            logger.info(f"BigQuery Total Fetch Time (Parallel): {elapsed:.3f}s")
            return result
        except Exception as e:
            logger.error(f"Failed to fetch aggregated civic data: {e}")
            return self._load_fallback_data()

    def get_debug_info(self) -> dict:
        if not self.client:
            return {"status": "disconnected", "dataset": self.dataset_id, "error": "Client not initialized."}
            
        try:
            tables_query = f"SELECT table_name FROM `{self.project_id}.{self.dataset_id}.INFORMATION_SCHEMA.TABLES`"
            tables_result = self._execute_query(tables_query)
            tables = [t['table_name'] for t in tables_result]
            
            sample_counts = {}
            for t in tables:
                if t in ['transport_density', 'environmental_stress', 'accessibility_incidents', 'community_sentiment', 'community_missions']:
                    count_q = f"SELECT COUNT(*) as cnt FROM `{self.project_id}.{self.dataset_id}.{t}`"
                    cnt_res = self._execute_query(count_q)
                    sample_counts[t] = cnt_res[0]['cnt'] if cnt_res else 0
                    
            return {
                "status": "connected",
                "dataset": self.dataset_id,
                "tables": tables,
                "sample_counts": sample_counts
            }
        except Exception as e:
            return {"status": "error", "dataset": self.dataset_id, "error": str(e)}

    def _load_fallback_data(self) -> dict:
        if os.path.exists(self.fallback_data_path):
            try:
                with open(self.fallback_data_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to parse fallback mock feeds: {e}")
        return {}
