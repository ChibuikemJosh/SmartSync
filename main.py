import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.ocr import router as ocr_router
from routes.squad import router as squad_router
from routes.voice import router as voice_router

app = FastAPI(title="SmartSync API")
allowed_origins = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(squad_router)
app.include_router(ocr_router)
app.include_router(voice_router)
