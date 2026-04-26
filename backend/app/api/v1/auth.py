"""认证路由 - /api/v1/auth"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session

from app.core.db import get_session
from app.services.auth import get_current_user, login_user, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


class AuthRequest(BaseModel):
    username: str
    password: str
    target_role: str = "general"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/register", response_model=TokenResponse)
def register(body: AuthRequest, session: Session = Depends(get_session)):
    user = register_user(body.username, body.password, session, target_role=body.target_role)
    token = login_user(body.username, body.password, session)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(body: AuthRequest, session: Session = Depends(get_session)):
    token = login_user(body.username, body.password, session)
    return TokenResponse(access_token=token)


@router.get("/me")
def me(user=Depends(get_current_user)):
    return {
        "id": user.id,
        "username": user.username,
        "target_style": user.target_style,
        "humor_weight": user.humor_weight,
        "voice_input_enabled": user.voice_input_enabled,
        "target_role": user.target_role,
    }
