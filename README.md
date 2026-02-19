# WhatsApp Custom LLM (Ollama) + Meta Cloud API (FastAPI)

A clean, local-first WhatsApp auto-reply backend powered by:

- FastAPI
- Meta WhatsApp Cloud API
- Ollama (local LLM)
- SQLite (conversation history + idempotency)

This project runs entirely locally and does not rely on cloud LLM providers.

---

## ✨ Features

- Meta webhook verification (GET)
- Webhook signature verification (HMAC SHA-256, enforced)
- Idempotency protection (prevents duplicate replies)
- Per-sender rate limiting
- SQLite conversation history
- English-only WhatsApp chat style
- Local LLM via Ollama

---

## 🧱 Architecture Overview

Incoming WhatsApp message  
→ Meta Webhook  
→ FastAPI backend  
→ Ollama (local LLM)  
→ Meta Graph API  
→ Reply sent back to WhatsApp  

---

# 🚀 How to Use (Local)

## 1) Install dependencies

```bash
pip install -r requirements.txt
```

---

## 2) Configure `.env`

This repository includes a tracked `.env` template.

Fill in the required values:

```env
META_WA_VERIFY_TOKEN=
META_APP_SECRET=
META_WA_ACCESS_TOKEN=
META_WA_PHONE_NUMBER_ID=
META_GRAPH_API_VERSION=v25.0

OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.1:8b-instruct-q8_0

SQLITE_PATH=./app_data.sqlite
RATE_LIMIT_WA_PER_MINUTE=10
```

Never commit real tokens or secrets.

---

## 3) Start Ollama

Make sure Ollama is installed and running:

```bash
ollama serve
```

Pull the model if needed:

```bash
ollama pull llama3.1:8b-instruct-q8_0
```

---

## 4) Run the FastAPI server

From the project root:

```bash
uvicorn main:app --reload
```

Server runs at:

```
http://127.0.0.1:8000
```

---

## 5) Expose your local server (Cloudflare Tunnel)

In a second terminal:

```bash
cloudflared tunnel --url http://127.0.0.1:8000
```

You will receive a public HTTPS URL like:

```
https://random-name.trycloudflare.com
```

---

## 6) Configure Meta Webhook

Go to:

Meta Developer Dashboard  
→ Your App  
→ WhatsApp  
→ Configuration (or API Setup)

### Webhook Settings

Callback URL:

```
https://YOUR_TUNNEL_URL/meta/whatsapp/webhook
```

Verify Token:

Must match your `.env` value:
```
META_WA_VERIFY_TOKEN
```

Subscribe to:
- messages

If you restart the Cloudflare quick tunnel, the URL changes.  
Update the callback URL in Meta again.

---

## 7) Test

Send a message to your WhatsApp test number.

If configured correctly:
- Webhook receives event
- Ollama generates reply
- Meta sends reply back to WhatsApp

---

# 🔐 Where to Get Meta Keys

All values are available in Meta Developer Dashboard.

---

## META_WA_VERIFY_TOKEN

You create this manually.  
Any random string works.  
It must match the value entered in the Webhook "Verify Token" field.

---

## META_APP_SECRET

Meta Dashboard  
→ App  
→ Settings  
→ Basic  
→ App Secret  

Click "Show" if needed.

---

## META_WA_ACCESS_TOKEN

Meta Dashboard  
→ WhatsApp  
→ API Setup  

Generate a temporary access token for testing.

For production use, implement long-lived token handling.

---

## META_WA_PHONE_NUMBER_ID

Meta Dashboard  
→ WhatsApp  
→ API Setup  

Displayed near your test number and WhatsApp Business Account information.

---

# ⚙️ Rate Limiting Behavior

To prevent Meta from retrying webhook deliveries, the server always returns:

```
200 OK
```

Even if rate limits are hit.

When rate limited:
- The webhook is acknowledged
- No reply is generated
- This prevents duplicate Meta retries

---

# 🗄️ Local Database

Conversation history and idempotency are stored in:

```
app_data.sqlite
```

To reset history:

```bash
rm -f app_data.sqlite
```

---

# 🧾 Notes

- Default Graph API version: **v25.0**
- Update `META_GRAPH_API_VERSION` if Meta deprecates it.
- This project is intended as a local demo backend.
- No cloud LLM usage is included.

---

# 📜 License

MIT (or your preferred license)
