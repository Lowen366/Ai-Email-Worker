# AI Email Worker (FastAPI on Render)

## Deploy
1. Create a new GitHub repo and add these files.
2. On Render, click **New +** → **Blueprint** → select this repo. (render.yaml will be detected.)
3. After deploy, note the public URL, e.g. `https://ai-email-worker.onrender.com`.

## Test
```bash
curl -s -X POST "$URL/write-email" \
-H 'Content-Type: application/json' \
-d '{
"goal": "win-back lapsed customer with accessory suggestion",
"offer": "Free shipping this week",
"cta_url": "https://yourbrand.com/solar-lamp-accessories",
"customer": {
"id": "cus_123",
"name": "Avery Park",
"email": "avery@example.com",
"locale": "en-GB",
"segment": ["eco-conscious","repeat-buyer"],
"purchase_history": [{"sku":"SOLAR-LAMP-2","date":"2025-08-02","price":39.95}],
"interests": ["off-grid","small-space"],
"lifecycle_stage": "lapsed",
"constraints": {"do_not_mention": ["budget"], "format":"html"}
}
}' | jq .
