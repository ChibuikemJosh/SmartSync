from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# Import routes
from routes.squad import router as squad_router
#from routes.ai import router as ai_router
from routes.health import router as health_router
import uvicorn
from services.database import GraphService

# Import your routes
from routes import ai, auth, chat, health, squad, transactions

app = FastAPI(
    title="SmartSync API",
    description="Backend for AI-powered Trust Score and Financial Management",
    version="2.0.0"
)

# --- CORS MIDDLEWARE ---
# This is CRUCIAL for the Expo app to talk to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace "*" with your app's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MOUNT ROUTES ---
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(ai.router, prefix="/ai", tags=["AI & OCR"])
app.include_router(chat.router, prefix="/chat", tags=["AI Advisor"])
app.include_router(squad.router, prefix="/payments", tags=["Squad Payments"])
app.include_router(transactions.router, prefix="/transactions", tags=["Ledger"])
app.include_router(health.router, prefix="/health", tags=["System Health"])

@app.get("/")
async def root():
    return {
        "project": "SmartSync",
        "status": "Online",
        "message": "Welcome to the SmartSync API. See /docs for Swagger UI."
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)