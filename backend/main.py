from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
import uvicorn

from routes import auth, health, squad, transactions
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

# Lazy import AI routes to avoid loading model at startup
try:
    from routes import ai, chat
    ai_available = True
except Exception as e:
    ai_available = False
    print(f"⚠️ AI routes unavailable: {e}")

app = FastAPI(
    title="SmartSync API",
    description="Backend for AI-powered Trust Score and Financial Management",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(squad.router, prefix="/payments", tags=["Squad Payments"])
app.include_router(transactions.router, prefix="/transactions", tags=["Ledger"])
app.include_router(health.router, prefix="/health", tags=["System Health"])


# Startup checks to log env presence and DB connectivity
@app.on_event("startup")
async def startup_checks():
    keys = ["NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD", "AUTH_SECRET_KEY", "SECRET_KEY"]
    for k in keys:
        logging.info("Env %s present: %s", k, bool(os.getenv(k)))

    try:
        from services.database import GraphService
        gs = GraphService()
        logging.info("GraphService available: %s", gs.is_available())
        gs.close()
    except Exception as e:
        logging.warning("DB connectivity check failed: %s", e)

if ai_available:
    app.include_router(ai.router, prefix="/ai", tags=["AI & OCR"])
    app.include_router(chat.router, prefix="/chat", tags=["AI Advisor"])

@app.get("/")
async def root():
    return {
        "project": "SmartSync",
        "status": "Online",
        "message": "Welcome to the SmartSync API. See /docs for Swagger UI."
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    reload_env = os.getenv("RELOAD", "True").lower() in ("true", "1", "yes")
    uvicorn.run("main:app", host=host, port=port, reload=reload_env)


# Ensure that unexpected exceptions return JSON with CORS headers so browsers
# don't drop responses when intermediaries replace 500s.
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logging.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*",
        },
    )
