from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any

class Customer(BaseModel):
id: str
name: Optional[str] = None
email: Optional[str] = None
locale: Optional[str] = "en-GB"
segment: Optional[List[str]] = None
last_interaction: Optional[str] = None
purchase_history: Optional[List[Dict[str, Any]]] = None
interests: Optional[List[str]] = None
lifecycle_stage: Optional[str] = None
cart: Optional[Dict[str, Any]] = None
constraints: Optional[Dict[str, Any]] = None

class RequestBody(BaseModel):
goal: str
offer: Optional[str] = None
cta_url: Optional[HttpUrl] = None
constraints: Optional[Dict[str, Any]] = None
customer: Customer

class EmailResponse(BaseModel):
subject: str = Field(max_length=64)
preheader: str = Field(max_length=110)
greeting: str
body_text: str
body_html: str
cta_text: str
cta_url: HttpUrl
notes: str
