"""认证路由 - /api/v1/auth"""

import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from app.core.db import get_session
from app.data.styles import get_all_styles
from app.services.auth import VALID_ROLES, get_current_user, login_user, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


class AuthRequest(BaseModel):
    username: str
    password: str
    target_role: str = "general"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class StylesRequest(BaseModel):
    target_styles: list[str]  # e.g. ["huangbo", "hejiong", "caikangyong"]


class RoleUpdateRequest(BaseModel):
    target_role: str


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
    try:
        styles = json.loads(user.target_styles) if user.target_styles else []
    except Exception:
        styles = []
    return {
        "id": user.id,
        "username": user.username,
        "target_style": user.target_style,
        "target_styles": styles,
        "humor_weight": user.humor_weight,
        "voice_input_enabled": user.voice_input_enabled,
        "target_role": user.target_role,
    }


@router.put("/role")
def update_role(
    body: RoleUpdateRequest,
    user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """切换当前账号的目标角色（医美/装修/物业/通用）"""
    if body.target_role not in VALID_ROLES:
        raise HTTPException(400, "无效的身份")
    user.target_role = body.target_role
    session.add(user)
    session.commit()
    return {"ok": True, "target_role": body.target_role}


@router.put("/styles")
def update_styles(
    body: StylesRequest,
    user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """保存用户选择的 3 个风格路线"""
    from app.data.styles import STYLES
    valid = [s for s in body.target_styles if s in STYLES]
    if len(valid) < 1:
        from fastapi import HTTPException
        raise HTTPException(400, "至少选择 1 个风格")
    valid = valid[:5]  # 最多 5 个
    user.target_styles = json.dumps(valid, ensure_ascii=False)
    if valid and not user.target_style:
        user.target_style = valid[0]
    session.add(user)
    session.commit()
    return {"ok": True, "target_styles": valid}


@router.get("/styles")
def list_styles():
    """返回 8 个风格的详细信息供选择"""
    return {"styles": get_all_styles()}
