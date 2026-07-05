import os
import logging
import json

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.client = None
        # Upgraded to Gemini 2.5 Flash for live AI pipeline
        self.model_name = "gemini-2.5-flash"
        
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                
                # We configure generation config to hint at JSON output
                # Using standard parameters for robust execution
                self.client = genai.GenerativeModel(self.model_name)
                logger.info(f"Gemini Client ({self.model_name}) initialized successfully.")
            except ImportError:
                logger.warning("google-generativeai package not found. Running in mock simulation mode.")
            except Exception as e:
                logger.error(f"Error configuring Gemini client: {e}")
        else:
            logger.info("No GEMINI_API_KEY environment variable set. Running in mock simulation mode.")

    def generate_json_content(self, prompt: str, retries: int = 1) -> dict:
        """
        Sends a prompt to the Gemini API, forcing a structured JSON parse.
        If the response is malformed, it retries once.
        Returns a dict if successful, None if all retries fail.
        """
        if not self.client:
            return None
            
        for attempt in range(retries + 1):
            try:
                # Ask model explicitly to return valid JSON
                generation_config = {"response_mime_type": "application/json"}
                response = self.client.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                
                if response and response.text:
                    try:
                        return json.loads(response.text)
                    except json.JSONDecodeError:
                        logger.warning(f"Attempt {attempt + 1}: Gemini returned invalid JSON. Retrying.")
                        continue # loop to retry
                        
                logger.warning(f"Attempt {attempt + 1}: Gemini API returned empty response.")
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1}: Gemini API execution failed: {e}.")
                # If it's a quota or network error, retrying might not help, but we try once.
        
        logger.error("All Gemini API attempts failed or returned malformed JSON. Falling back.")
        return None

    def generate_text_content(self, prompt: str, retries: int = 1) -> str:
        """Standard text generation for chat workflows."""
        if not self.client:
            return None
            
        for attempt in range(retries + 1):
            try:
                response = self.client.generate_content(prompt)
                if response and response.text:
                    return response.text
            except Exception as e:
                logger.error(f"Attempt {attempt + 1}: Gemini API execution failed: {e}.")
        
        return None
