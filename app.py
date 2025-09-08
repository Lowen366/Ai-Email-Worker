import os, json
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import AnyUrl

from schema import RequestBody, EmailResponse
from prompts import build_system_prompt, build_task_prompt

app = FastAPI(title="AI Email Worker", version="0.2.0")

# CORS – narrow to your website domains in production
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
def call_llm(system_prompt: str, task_prompt: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    MOCK_MODE: deterministic but grounded in provided `recommendations`.
    Non-mock path: wire your provider here later.
    """
    if MOCK_MODE or not API_KEY:
        customer = (payload or {}).get("customer", {}) if payload else {}
        name = (customer.get("name") or "there").strip() or "there"

        recs = (payload or {}).get("recommendations", []) if payload else []
        def _p(v):
            try: return f"£{float(v):.2f}"
            except Exception: return ""
        bullets_txt, bullets_html = [], []
        for r in recs[:5]:
            nm = (r.get("name") or "item").strip()
            pr = _p(r.get("price"))
            url = (r.get("url") or "").strip()
            label = f"{nm}" + (f" — {pr}" if pr else "")
            bullets_txt.append(f"- {label}" + (f" ({url})" if url else ""))
            bullets_html.append(f"<li><a href=\"{url}\">{label}</a></li>" if url else f"<li>{label}</li>")

        bullets_txt = "\n".join(bullets_txt) if bullets_txt else "- (No suitable items found yet)"
        bullets_html = "<ul>" + "".join(bullets_html) + "</ul>" if bullets_html else "<p><em>(No suitable items found yet)</em></p>"

        subject = f"Your picks, {name}"
        preheader = "A few items we think you’ll like."
        greeting = f"Hi {name},"
        body_text = (
            f"{greeting}\n\n"
            "We picked a few things based on your interests:\n\n"
            f"{bullets_txt}\n\n"
            "If you have any questions, just hit reply.\n\n"
            "Best,\nCustomer Success"
        )
        body_html = (
            f"<p>{greeting}</p>"
            f"<p>We picked a few things based on your interests:</p>"
            f"{bullets_html}"
            "<p style='margin-top:12px;color:#555'>Best,<br>Customer Success</p>"
        )

        return {
            "subject": subject,
            "preheader": preheader,
            "greeting": greeting,
            "body_text": body_text,
            "body_html": body_html,
            "cta_text": "View details",
            "cta_url": (payload or {}).get("cta_url") or CTA_FALLBACK,
            "notes": "MOCK grounded: built from provided recommendations"
        }

    # Real provider goes here later
    provider = MODEL_PROVIDER.lower()
    raise HTTPException(501, f"Provider '{provider}' not wired yet. Set MOCK_MODE=true to test.")

@app.get("/")
def root():
    return {"ok": True, "service": "ai-email-worker", "version": "0.2.0"}

@app.post("/write-email", response_model=EmailResponse)
def write_email(body: RequestBody):
    system_prompt = build_system_prompt()
    task_prompt = build_task_prompt(body)
    try:
        result = call_llm(system_prompt, task_prompt, payload=body.model_dump())
        email = EmailResponse(**result)
        # prefer caller CTA; otherwise fallback
        effective_cta = body.cta_url or AnyUrl(CTA_FALLBACK, scheme="https")
        email.cta_url = effective_cta
        return email
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Generation failed: {e}")
