"""FastAPI 앱 진입점"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from app.routers import sessions, items, exports, brands

app = FastAPI(
    title="JH-견적시스템 API",
    version="1.0.0",
    description="인테리어 견적 AI 에이전트 자동화 시스템",
)

# CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(sessions.router, prefix="/api/v1")
app.include_router(items.router, prefix="/api/v1")
app.include_router(exports.router, prefix="/api/v1")
app.include_router(brands.router, prefix="/api/v1")


@app.get("/")
async def health_check():
    return {
        "status": "ok",
        "service": "JH-견적시스템 API",
        "version": "1.0.0",
    }
