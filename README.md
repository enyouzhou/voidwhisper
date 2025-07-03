# AI-Quote Demo  :zap:

Generate witty/cynical "anti-inspirational" English quotes with matching images – all locally runnable.

---

## 1. Project Goals
1. Generate a short, humorous "poison-chicken-soup" quote based on a topic
2. Render a poster-style image containing (or inspired by) that quote
3. Serve a web page that lets the user click **Generate** and immediately see the result
4. Store each result (quote + image URL) for later display / sharing (optional at demo stage)

---

## 2. Tech Stack
| Layer          | Choice                                                    | Why |
|----------------|-----------------------------------------------------------|-----|
| LLM (quote)    | **GPT-4o-mini** via OpenAI compatible API                | High quality, zero fine-tune cost |
| Image model    | **Flux Kontext Pro** (Stable-Diffusion variant) API      | Fast, high-fidelity posters |
| Backend        | Python **Flask 3**                                       | Lightweight, easy to extend with Blueprints |
| Frontend       | Vanilla **HTML + CSS + JS** (component templates)        | Minimal dependencies, easy later migration to React / Vue |
| Database       | **PostgreSQL** via **Supabase** SDK (optional)           | Free tier, REST / Realtime, object storage |

> ⚠ For the first local demo we can skip Supabase and just save images to `output/`.

---

## 3. Repository Structure
```
ai-quote-demo/
├─ backend/
│   ├─ app.py                # Flask entry-point
│   ├─ config.py             # Read .env → settings object
│   ├─ routers/
│   │   └─ quote.py          # /api/quote Blueprint
│   └─ services/
│       ├─ gpt_client.py     # GPT-4o-mini wrapper
│       ├─ flux_client.py    # Flux image wrapper
│       └─ supabase_client.py# DB + storage helper (optional)
│
├─ frontend/
│   ├─ index.html            # UI
│   ├─ css/
│   │   └─ styles.css
│   ├─ js/
│   │   └── api.js           # fetch & DOM update
│   └─ components/           # HTML <template> snippets
│       ├─ QuoteCard.html
│       └─ Loader.html
│
├─ .env                      # local secrets (NOT committed)
└─ requirements.txt          # backend dependencies
```

---

## 4. Environment Variables (`.env`)
```bash
# OpenAI / GPT-4o-mini
OPENAI_API_KEY=sk-…
OPENAI_BASE_URL=https://api.tu-zi.com/v1

# Flux image API
FLUX_API_KEY=sk-…

# (optional) Supabase
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=sbp-…
```

Load once at startup via `python-dotenv` inside `backend/config.py`:
```python
from dotenv import load_dotenv; load_dotenv()
import os
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
…
```

---

## 5. Backend Flow
```mermaid
sequenceDiagram
    autonumber
    User→>Frontend: click "Generate"
    Frontend→>Flask /quote API: GET /api/quote?topic=love
    Note right of Flask: routers/quote.py
    Flask→>GPT Service: generate_quote(topic)
    GPT Service->>OpenAI API: /chat/completions (GPT-4o-mini)
    GPT Service-->>Flask: quote text
    Flask→>Flux Service: generate_image(quote)
    Flux Service->>Flux API: /v1/images/generations
    Flux Service-->>Flask: image_url
    Flask→>Supabase (optional): save(quote, image_url)
    Flask-->>Frontend: {quote, image_url}
    Frontend→>User: render card + poster
```

---

## 6. Backend Quick Start
```bash
# 0) clone repo & cd ai-quote-demo
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in keys

# 1) run the server
python backend/app.py  # default http://127.0.0.1:5000
```

Endpoint description:
```
GET /api/quote?topic=<topic>
→ 200 JSON { "quote": "…", "img_url": "…" }
```

---

## 7. Frontend Quick Start
_No build tools needed._
```bash
cd frontend
python -m http.server 8000  # or just open index.html in browser
```
The page loads `/api/quote` via relative URL so it works on localhost.

---

## 8. Component Guidelines
1. **UI components** live in `frontend/components/` as `<template>` blocks → JS clones them; later they can slide into a framework with minimal rewrite.
2. **Service layer**: each external integration in its own file under `backend/services/`.
3. **Blueprints**: every API domain (quote, auth, gallery…) gets its own blueprint.

---

## 9. Development Checklist
- [ ] `services/gpt_client.py` – wrap `OpenAI` call (`model="gpt-4o-all"`)
- [ ] `services/flux_client.py` – POST to `/v1/images/generations`, handle polling if async
- [ ] `routers/quote.py` – orchestrate + optional Supabase save
- [ ] Minimal `frontend/index.html` with `Generate` button & result card
- [ ] README (this file) ✅

---

## 10. Next Steps
1. Initial local demo → verify quality & latency
2. Add Supabase storage + "My Quotes" gallery view
3. Switch frontend to React/Vue if needed, preserving API contract
4. Consider fine-tuning or local models for cost optimisation
5. Deploy: Fly.io / Railway for Flask + Vercel (static) or full-stack on Render

Happy hacking! :rocket: 