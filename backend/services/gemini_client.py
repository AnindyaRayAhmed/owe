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
class GeminiException(Exception): pass
class GeminiTimeoutError(GeminiException): pass
class GeminiQuotaError(GeminiException): pass
class GeminiAuthError(GeminiException): pass
class GeminiInvalidJSONError(GeminiException): pass
class GeminiGeneralError(GeminiException): pass


class GeminiClient:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.client = None
        self.model_name = "gemini-2.5-flash"
        self.errors = []
        
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
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

    def _extract_json(self, text: str) -> str:
        """Helper to extract JSON payload from text that might contain markdown blocks."""
        text = text.strip()
        first_brace = text.find('{')
        first_bracket = text.find('[')
        
        start_idx = -1
        end_char = ''
        if first_brace != -1 and (first_bracket == -1 or first_brace < first_bracket):
            start_idx = first_brace
            end_char = '}'
        elif first_bracket != -1:
            start_idx = first_bracket
            end_char = ']'
            
        if start_idx == -1:
            return text
            
        end_idx = text.rfind(end_char)
        if end_idx != -1:
            return text[start_idx:end_idx + 1]
            
        return text

    def generate_json_content(self, prompt: str, retries: int = 1) -> dict:
        """
        FAIL-FAST PATH: No retries for network/auth/quota issues. Only retries once for JSON parse errors.
        Limits tokens to 500 max to dramatically reduce generation latency.
        """
        if not self.client:
            raise GeminiAuthError(f"Gemini client uninitialized. Errors: {self.errors}")
            
        # Append strict instructions for concise output
        json_instruction = "\n\nCRITICAL: Return ONLY a valid JSON object or list. Keep the response under 100 words. No markdown formatting outside the JSON."
        full_prompt = prompt + json_instruction
            
        json_failures = 0
        for attempt in range(retries + 1):
            start_time = time.time()
            try:
                # Add performance constraints: limit max output tokens
                import google.generativeai as genai
                generation_config = genai.types.GenerationConfig(max_output_tokens=500)
                
                response = self.client.generate_content(
                    full_prompt,
                    generation_config=generation_config
                )
                
                latency = time.time() - start_time
                logger.info(f"Gemini API Response Time: {latency:.3f}s")
                
                if response and response.text:
                    try:
                        clean_text = self._extract_json(response.text)
                        return json.loads(clean_text)
                    except json.JSONDecodeError as je:
                        logger.warning(f"Gemini returned invalid JSON. Retrying JSON parse loop...")
                        json_failures += 1
                        if json_failures >= 2:
                            raise GeminiInvalidJSONError("Gemini returned invalid JSON twice.") from je
                        continue
                        
                raise GeminiInvalidJSONError("Gemini returned empty response.")
                
            except Exception as e:
                # Bypass standard retries to fail fast to deterministic fallback
                if isinstance(e, GeminiException) and not isinstance(e, GeminiInvalidJSONError):
                    raise e
                if isinstance(e, GeminiInvalidJSONError) and attempt < retries:
                    continue # only retry JSON failures
                    
                err_type = type(e).__name__
                if "DeadlineExceeded" in err_type or "Timeout" in err_type:
                    raise GeminiTimeoutError(f"API timeout: {e}") from e
                elif "ResourceExhausted" in err_type or "Quota" in err_type:
                    raise GeminiQuotaError(f"API quota: {e}") from e
                elif "PermissionDenied" in err_type or "Unauthenticated" in err_type:
                    raise GeminiAuthError(f"API auth failed: {e}") from e
                else:
                    raise GeminiGeneralError(f"API failed: {e}") from e

    def generate_text_content(self, prompt: str, retries: int = 0) -> str:
        """Fail-fast text generation. No retries."""
        if not self.client:
            raise GeminiAuthError(f"Gemini uninitialized: {self.errors}")
            
        start_time = time.time()
        try:
            import google.generativeai as genai
            generation_config = genai.types.GenerationConfig(max_output_tokens=500)
            response = self.client.generate_content(prompt, generation_config=generation_config)
            
            logger.info(f"Gemini API Text Latency: {time.time() - start_time:.3f}s")
            
            if response and response.text:
                return response.text
            raise GeminiGeneralError("Empty response.")
        except Exception as e:
            raise GeminiGeneralError(f"API failed: {e}") from e
