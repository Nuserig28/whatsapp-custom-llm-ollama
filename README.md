# WhatsApp Custom LLM (Ollama) Backend

This project is designed as a local-first WhatsApp AI backend using Ollama and does not include cloud LLM usage.

## Features
- Webhook verification (hub.challenge flow)
- Webhook receiver (optional X-Hub-Signature-256)
- Idempotency (prevents duplicate processing)
- Conversation memory (SQLite)
- Local LLM replies via Ollama (no paid API required)
- Sends replies back via WhatsApp Cloud API

## Endpoints
- GET  `/meta/whatsapp/webhook`
- POST `/meta/whatsapp/webhook`
- GET  `/health`

## Environment Variables

```bash
# Meta webhook verification
META_WA_VERIFY_TOKEN=your_verify_token

# Meta signature verification (optional but supported)
META_APP_SECRET=your_app_secret

# Meta send message (Cloud API)
META_WA_ACCESS_TOKEN=your_access_token
META_WA_PHONE_NUMBER_ID=your_phone_number_id
META_GRAPH_API_VERSION=v25.0

# Ollama (local)
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.1:8b

# Storage
SQLITE_PATH=./app_data.sqlite
