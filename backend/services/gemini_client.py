import os
import logging
import json
import time

logger = logging.getLogger(__name__)

try:
    from google.api_core import exceptions as google_exceptions
except ImportError:
    google_exceptions = None

# --- Custom Gemini Exceptions ---
class GeminiException(Exception):
    """Base exception for Gemini client errors."""
    pass

class GeminiTimeoutError(GeminiException):
    """Raised when a timeout occurs during the Gemini request."""
    pass

class GeminiQuotaError(GeminiException):
    """Raised when the Gemini quota is exceeded."""
    pass

class GeminiAuthError(GeminiException):
    """Raised when there's an authentication or API key configuration issue."""
    pass

class GeminiInvalidJSONError(GeminiException):
    """Raised when Gemini returns invalid JSON repeatedly."""
    pass

class GeminiGeneralError(GeminiException):
    """Raised for any other general exceptions thrown by the Gemini API."""
    pass


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
        Returns a dict if successful, or raises a GeminiException.
        """
        if not self.client:
            raise GeminiAuthError(f"Gemini client is uninitialized. Configuration errors: {self.errors}")
            
        json_failures = 0
        for attempt in range(retries + 1):
            start_time = time.time()
            try:
                # Ask model explicitly to return valid JSON
                generation_config = {"response_mime_type": "application/json"}
                response = self.client.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                
                latency = time.time() - start_time
                logger.info(f"Gemini API attempt {attempt + 1} latency: {latency:.3f} seconds")
                
                if response and response.text:
                    try:
                        return json.loads(response.text)
                    except json.JSONDecodeError as je:
                        logger.warning(f"Attempt {attempt + 1}: Gemini returned invalid JSON. Retrying.")
                        json_failures += 1
                        if json_failures >= 2:
                            raise GeminiInvalidJSONError("Gemini returned invalid JSON twice.") from je
                        continue
                        
                logger.warning(f"Attempt {attempt + 1}: Gemini API returned empty response.")
                json_failures += 1
                if json_failures >= 2:
                    raise GeminiInvalidJSONError("Gemini returned empty response / invalid JSON twice.")
                
            except Exception as e:
                if isinstance(e, GeminiException):
                    raise e
                    
                err_type = type(e).__name__
                is_timeout = False
                is_quota = False
                is_auth = False
                
                if google_exceptions:
                    if isinstance(e, (google_exceptions.DeadlineExceeded, google_exceptions.ServiceUnavailable)):
                        is_timeout = True
                    elif isinstance(e, google_exceptions.ResourceExhausted):
                        is_quota = True
                    elif isinstance(e, (google_exceptions.PermissionDenied, google_exceptions.Unauthenticated)):
                        is_auth = True
                
                if "DeadlineExceeded" in err_type or "Timeout" in err_type or "Deadline Exceeded" in str(e):
                    is_timeout = True
                elif "ResourceExhausted" in err_type or "Quota" in err_type or "QuotaExceeded" in err_type:
                    is_quota = True
                elif "PermissionDenied" in err_type or "Unauthenticated" in err_type or "API_KEY_INVALID" in str(e) or "API key not valid" in str(e):
                    is_auth = True
                
                if is_timeout:
                    logger.error(f"Attempt {attempt + 1}: Gemini API request timed out: {e}")
                    if attempt == retries:
                        raise GeminiTimeoutError(f"Gemini API request timed out: {e}") from e
                elif is_quota:
                    logger.error(f"Attempt {attempt + 1}: Gemini API quota exceeded: {e}")
                    if attempt == retries:
                        raise GeminiQuotaError(f"Gemini API quota exceeded: {e}") from e
                elif is_auth:
                    logger.error(f"Attempt {attempt + 1}: Gemini API authentication failed: {e}")
                    if attempt == retries:
                        raise GeminiAuthError(f"Gemini API authentication failed: {e}") from e
                else:
                    logger.error(f"Attempt {attempt + 1}: Gemini API execution failed: {e}")
                    if attempt == retries:
                        raise GeminiGeneralError(f"Gemini API execution failed: {e}") from e

    def generate_text_content(self, prompt: str, retries: int = 1) -> str:
        """Standard text generation for chat workflows."""
        if not self.client:
            raise GeminiAuthError(f"Gemini client is uninitialized. Configuration errors: {self.errors}")
            
        for attempt in range(retries + 1):
            start_time = time.time()
            try:
                response = self.client.generate_content(prompt)
                latency = time.time() - start_time
                logger.info(f"Gemini API text attempt {attempt + 1} latency: {latency:.3f} seconds")
                if response and response.text:
                    return response.text
                logger.warning(f"Attempt {attempt + 1}: Gemini API returned empty text response.")
                if attempt == retries:
                    raise GeminiGeneralError("Gemini returned empty text response.")
            except Exception as e:
                err_type = type(e).__name__
                is_timeout = False
                is_quota = False
                is_auth = False
                
                if google_exceptions:
                    if isinstance(e, (google_exceptions.DeadlineExceeded, google_exceptions.ServiceUnavailable)):
                        is_timeout = True
                    elif isinstance(e, google_exceptions.ResourceExhausted):
                        is_quota = True
                    elif isinstance(e, (google_exceptions.PermissionDenied, google_exceptions.Unauthenticated)):
                        is_auth = True
                
                if "DeadlineExceeded" in err_type or "Timeout" in err_type or "Deadline Exceeded" in str(e):
                    is_timeout = True
                elif "ResourceExhausted" in err_type or "Quota" in err_type or "QuotaExceeded" in err_type:
                    is_quota = True
                elif "PermissionDenied" in err_type or "Unauthenticated" in err_type or "API_KEY_INVALID" in str(e) or "API key not valid" in str(e):
                    is_auth = True
                
                if is_timeout:
                    logger.error(f"Attempt {attempt + 1}: Gemini API request timed out: {e}")
                    if attempt == retries:
                        raise GeminiTimeoutError(f"Gemini API request timed out: {e}") from e
                elif is_quota:
                    logger.error(f"Attempt {attempt + 1}: Gemini API quota exceeded: {e}")
                    if attempt == retries:
                        raise GeminiQuotaError(f"Gemini API quota exceeded: {e}") from e
                elif is_auth:
                    logger.error(f"Attempt {attempt + 1}: Gemini API authentication failed: {e}")
                    if attempt == retries:
                        raise GeminiAuthError(f"Gemini API authentication failed: {e}") from e
                else:
                    logger.error(f"Attempt {attempt + 1}: Gemini API execution failed: {e}")
                    if attempt == retries:
                        raise GeminiGeneralError(f"Gemini API execution failed: {e}") from e
