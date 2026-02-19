import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException

from app.config import get_settings
from app.conversation_store import ConversationStore
from app.idempotency_store import IdempotencyStore
from app.message_router import generate_reply
from app.meta_whatsapp_service import MetaWhatsAppService, MetaWhatsAppConfig, MetaWhatsAppAPIError
from app.rate_limiter import SlidingWindowRateLimiter

router = APIRouter()

settings = get_settings()

conversation_store = ConversationStore(settings.sqlite_path)
idempotency_store = IdempotencyStore(settings.sqlite_path)

meta_service = MetaWhatsAppService(
    MetaWhatsAppConfig(
        access_token=settings.meta_access_token,
        phone_number_id=settings.meta_phone_number_id,
        api_version=settings.meta_graph_api_version,
    )
)

rate_limiter = SlidingWindowRateLimiter()


def _get_signature_header(request: Request) -> str:
    sig = request.headers.get("x-hub-signature-256") or request.headers.get("X-Hub-Signature-256")
    return (sig or "").strip()


def verify_signature(request: Request, body: bytes) -> None:
    if not settings.meta_app_secret:
        raise HTTPException(status_code=500, detail="Server misconfigured: META_APP_SECRET missing")

    signature = _get_signature_header(request)
    if not signature:
        raise HTTPException(status_code=403, detail="Missing webhook signature")

    expected = "sha256=" + hmac.new(
        settings.meta_app_secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=403, detail="Invalid webhook signature")


@router.get("/meta/whatsapp/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == settings.meta_verify_token:
        return int(challenge)

    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/meta/whatsapp/webhook")
async def receive_message(request: Request):
    body = await request.body()
    verify_signature(request, body)

    # Signature OK => real Meta webhook.
    # From here on ALWAYS return 200 OK to stop Meta retries.
    data = await request.json()
    if "entry" not in data:
        return {"ok": True}

    try:
        entry = data["entry"][0]
        change = entry["changes"][0]
        value = change["value"]

        if "messages" not in value:
            return {"ok": True}

        message = value["messages"][0]
        from_number = message["from"]
        message_id = message["id"]

        if idempotency_store.seen(message_id):
            return {"ok": True}

        # Sender-based rate limit: ACK + DROP (prevents delayed "auto replies")
        if not rate_limiter.allow(f"wa:{from_number}", settings.rate_limit_wa_per_minute, 60):
            print(f"[RATE_LIMIT] wa={from_number} blocked (limit={settings.rate_limit_wa_per_minute}/min) msg_id={message_id}")
            idempotency_store.mark(message_id)
            return {"ok": True, "rate_limited": True}

        # Mark early to ensure no later reply due to retries
        idempotency_store.mark(message_id)

        if message.get("type") != "text":
            return {"ok": True}

        text_body = message["text"]["body"]
        user_key = f"wa:{from_number}"

        history = conversation_store.last_n(user_key, 10)
        reply = generate_reply(history, text_body)

        conversation_store.add(user_key, "user", text_body)
        conversation_store.add(user_key, "assistant", reply)

        try:
            meta_service.send_text_message(to=from_number, text=reply)
        except MetaWhatsAppAPIError:
            # ACK anyway (no retry). This prevents late "self messages".
            return {"ok": True, "send_failed": True}

        return {"ok": True}

    except Exception as e:
        print("Webhook error:", type(e).__name__)
        return {"ok": True, "error": True}
