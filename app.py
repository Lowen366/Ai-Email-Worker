# app.py
import os, json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

from schema import RequestBody, EmailResponse
from prompts import build_system_prompt, build_task_prompt

app = FastAPI(title="AI Email Worker", version="0.1.0")

# CORS – lock down later to your domain(s)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MOCK_MODE = os.getenv("MOCK_MODE", "true").lower() == "true"
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "mock")
API_KEY = os.getenv("LLM_API_KEY")
CTA_FALLBACK = os.getenv("CTA_FALLBACK", "https://example.com")

# ---------- LLM ----------
def call_llm(system_prompt: str, task_prompt: str) -> Dict[str, Any]:
    if MOCK_MODE or not API_KEY:
        # Deterministic mock so you can test without a key
        return {
            "subject": "A little boost for your eco-home",
            "preheader": "We picked something practical you might like.",
            "greeting": "Hi there,",
            "body_text": (
                "We noticed you enjoyed our solar lamp recently. We’ve curated a small accessory "
                "that extends battery life and makes setup easier.\n\n"
                "You can opt out anytime."
            ),
            "body_html": (
                "<p>We noticed you enjoyed our solar lamp recently.</p>"
                "<p>We’ve curated a small accessory that extends battery life and makes setup easier.</p>"
                "<p style='font-size:12px;color:#666'>You can opt out anytime.</p>"
            ),
            "cta_text": "See the accessory",
            "cta_url": CTA_FALLBACK,
            "notes": "MOCK: Replace with real LLM output when API key is set."
        }

    provider = MODEL_PROVIDER.lower()
    # TODO: wire your real provider call here
    raise HTTPException(501, f"Provider '{provider}' not wired yet. Set MOCK_MODE=true to test.")

@app.get("/")
def root():
    return {"ok": True, "service": "ai-email-worker", "version": "0.1.0"}

@app.post("/write-email", response_model=EmailResponse)
def write_email(body: RequestBody):
    system_prompt = build_system_prompt()
    task_prompt = build_task_prompt(body)
    try:
        result = call_llm(system_prompt, task_prompt)
        email = EmailResponse(**result)
        # Prefer caller CTA if provided; otherwise fallback
        email.cta_url = str(body.cta_url or CTA_FALLBACK)
        return email
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Generation failed: {e}")
