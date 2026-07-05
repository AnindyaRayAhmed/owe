from pydantic import BaseModel
from typing import Optional, List

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    source: Optional[str] = None

class GeminiDebugResponse(BaseModel):
    status: str
    mode: str
    key_configured: bool
    model: str
    errors: List[str]
