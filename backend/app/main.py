from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app.api.v1 import auth, diary, home, invite, practice, scenarios, skills, tts
from app.core.config import settings
from app.core.db import engine, init_db
from app.seed.loader import seed_all

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    with Session(engine) as session:
        result = seed_all(session)
        print(f"[seed] inserted: {result}")
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

# 全局异常处理 —— 避免 AI 超时/错误导致裸 500
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log.error("Unhandled exception on %s %s: %s", request.method, request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "服务暂时出了点问题，请稍后再试"},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router, prefix="/api/v1")
app.include_router(skills.router, prefix="/api/v1")
app.include_router(practice.router, prefix="/api/v1")
app.include_router(diary.router, prefix="/api/v1")
app.include_router(home.router, prefix="/api/v1")
app.include_router(scenarios.router, prefix="/api/v1")
app.include_router(tts.router, prefix="/api/v1")
app.include_router(invite.router, prefix="/api/v1")


@app.get("/")
def root():
    return {"app": settings.app_name, "status": "ok"}


@app.get("/health")
def health():
    return {"status": "healthy"}
