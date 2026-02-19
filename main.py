from fastapi import FastAPI
import uvicorn

from dotenv import load_dotenv

# Load .env from project root for BOTH:
# - `python main.py`
# - `uvicorn main:app --reload`
load_dotenv()

from app.meta_webhook_routes import router as meta_router  # noqa: E402

app = FastAPI()
app.include_router(meta_router)


@app.get("/health")
def health():
    return {"ok": True}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
