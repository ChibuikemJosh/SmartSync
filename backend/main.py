from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
import uvicorn

from routes import auth, health, squad, transactions

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
