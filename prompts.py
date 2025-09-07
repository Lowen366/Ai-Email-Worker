# prompts.py
import json
from schema import EmailResponse, RequestBody

BRAND = "YourBrand"
TONE_GUIDE = "Warm, concise, helpful; no hype; plain language."
VOICE_RULES = "Use British English spelling; avoid exclamation marks; be specific."
AUDIENCE = "Eco-conscious homeowners and renters aged 25–45."
PRODUCT = "Eco-friendly home goods with durable materials and low energy use."
PROHIBITED = ["medical claims", "financial guarantees"]

def build_system_prompt() -> str:
    return f"""You are an AI email copywriter for {BRAND}. Write persuasive, respectful, and legally compliant emails.
Requirements:
- Tone: {TONE_GUIDE}
- Voice rules: {VOICE_RULES}
- Audience: {AUDIENCE}
- Product: {PRODUCT}
- Compliance: include opt-out line; avoid {PROHIBITED}; never fabricate facts.
- Always produce valid JSON matching the schema provided.
"""

def build_task_prompt(payload: RequestBody) -> str:
    schema = EmailResponse.model_json_schema()
    return (
        "Goal: " + payload.goal + "\n" +
        "Customer profile: " + payload.customer.model_dump_json() + "\n" +
        "Constraints: " + json.dumps(payload.constraints or {}, ensure_ascii=False) + "\n" +
        "Offer/CTA: " + (payload.offer or "") + "\n" +
        "Language/Locale: " + (payload.customer.locale or "en-GB") + "\n" +
        "Return ONLY JSON that conforms to this schema (no extra keys, no prose):\n" +
        json.dumps(schema, ensure_ascii=False)
    )
