import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import uvicorn

# Local imports
from routes import auth, health, squad, transactions

# Initialize environment and logging
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Lazy Load AI Routes ---
# Avoids heavy model/client loading if the environment isn't properly configured
try:
    from routes import ai, chat
    ai_available = True
except Exception as e:
    ai_available = False
    logger.warning(f"⚠️ AI routes unavailable: {e}")


# --- Lifespan Management (Replaces deprecated @app.on_event) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup Logic ---
    logger.info("🚀 Starting up SmartSync API...")
    keys = ["NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD", "AUTH_SECRET_KEY"]
    for k in keys:
        logger.info(f"Env {k} present: {bool(os.getenv(k))}")

    try:
        from services.database import GraphService
        gs = GraphService()
        logger.info(f"GraphService available: {gs.is_available()}")
        gs.close()
    except Exception as e:
        logger.warning(f"DB connectivity check failed: {e}")
    
    # App is now running
    yield 
    
    # --- Shutdown Logic ---
    logger.info("🛑 Shutting down SmartSync API...")


# --- App Initialization ---
app = FastAPI(
    title="SmartSync API",
    description="Backend for AI-powered Trust Score and Financial Management",
    version="2.0.0",
    lifespan=lifespan
)


# --- Middlewares ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # NOTE: Restrict to your frontend URLs for production
    allow_credentials=False, # Must be False if origins is "*"
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Global Exception Handler ---
# Catch unexpected errors and format them nicely with CORS headers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong on our end (Internal Server Error)"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        },
    )


# --- Routers ---
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(squad.router, prefix="/payments", tags=["Squad Payments"])
app.include_router(transactions.router, prefix="/transactions", tags=["Ledger"])
app.include_router(health.router, prefix="/health", tags=["System Health"])

if ai_available:
    app.include_router(ai.router, prefix="/ai", tags=["AI & OCR"])
    app.include_router(chat.router, prefix="/chat", tags=["AI Advisor"])


# --- Root Endpoint ---
@app.get("/", tags=["Root"])
async def root():
    return {
        "project": "SmartSync",
        "status": "Online",
        "version": "2.0.0",
        "message": "Welcome to the SmartSync API. See /docs for Swagger UI."
    }


# --- Server Runner ---
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    # Cast reload to boolean safely
    reload_env = os.getenv("RELOAD", "True").lower() in ("true", "1", "yes")
    
    logger.info(f"Starting uvicorn on {host}:{port} (Reload: {reload_env})")
    uvicorn.run("main:app", host=host, port=port, reload=reload_env)