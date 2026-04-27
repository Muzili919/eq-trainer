from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from app.api.v1 import auth, diary, home, practice, scenarios, skills, tts
from app.core.config import settings
from app.core.db import engine, init_db
from app.seed.loader import seed_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    with Session(engine) as session:
        result = seed_all(session)
        print(f"[seed] inserted: {result}")
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

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


@app.get("/")
def root():
    return {"app": settings.app_name, "status": "ok"}


@app.get("/health")
def health():
    return {"status": "healthy"}
