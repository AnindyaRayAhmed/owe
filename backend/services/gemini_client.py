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
        self.errors = []
        
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                
                # We configure generation config to hint at JSON output
                # Using standard parameters for robust execution
                self.client = genai.GenerativeModel(self.model_name)
                
                masked_key = f"...{self.api_key[-4:]}" if len(self.api_key) > 4 else "***"
                logger.info(f"Gemini Client ({self.model_name}) initialized successfully with API key {masked_key}.")
            except ImportError:
                msg = "google-generativeai package not found. Running in mock simulation mode."
                logger.warning(msg)
                self.errors.append(msg)
            except Exception as e:
                msg = f"Error configuring Gemini client: {e}"
                logger.error(msg)
                self.errors.append(msg)
        else:
            msg = "No GEMINI_API_KEY environment variable set. Running in mock simulation mode."
            logger.info(msg)
            self.errors.append(msg)

    def get_debug_status(self) -> dict:
        return {
            "status": "active" if self.client else "fallback",
            "mode": "gemini" if self.client else "simulation",
            "key_configured": bool(self.api_key),
            "model": self.model_name,
            "errors": self.errors
        }

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
                err_type = type(e).__name__
                if "Quota" in err_type or "ResourceExhausted" in err_type:
                    logger.error(f"Attempt {attempt + 1}: Gemini API quota exceeded ({err_type}).")
                elif "Auth" in err_type or "PermissionDenied" in err_type:
                    logger.error(f"Attempt {attempt + 1}: Gemini API authentication failed ({err_type}).")
                elif "Timeout" in err_type or "DeadlineExceeded" in err_type:
                    logger.error(f"Attempt {attempt + 1}: Gemini API request timed out ({err_type}).")
                elif "InvalidArgument" in err_type:
                    logger.error(f"Attempt {attempt + 1}: Invalid argument (e.g. invalid model): {e}")
                else:
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
                err_type = type(e).__name__
                if "Quota" in err_type or "ResourceExhausted" in err_type:
                    logger.error(f"Attempt {attempt + 1}: Gemini API quota exceeded ({err_type}).")
                elif "Auth" in err_type or "PermissionDenied" in err_type:
                    logger.error(f"Attempt {attempt + 1}: Gemini API authentication failed ({err_type}).")
                elif "Timeout" in err_type or "DeadlineExceeded" in err_type:
                    logger.error(f"Attempt {attempt + 1}: Gemini API request timed out ({err_type}).")
                elif "InvalidArgument" in err_type:
                    logger.error(f"Attempt {attempt + 1}: Invalid argument (e.g. invalid model): {e}")
                else:
                    logger.error(f"Attempt {attempt + 1}: Gemini API execution failed: {e}.")
        
        return None
