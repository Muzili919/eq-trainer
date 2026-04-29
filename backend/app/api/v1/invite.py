"""邀请码路由 - /api/v1/invite"""

import secrets
import string
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.config import settings
from app.core.db import get_session
from app.models.invitation import InvitationCode
from app.models.user import User
from app.services.auth import get_current_user

router = APIRouter(prefix="/invite", tags=["invite"])

FREE_DAILY_PRACTICE_LIMIT = 3


def _generate_code(prefix: str = "EQ", length: int = 6) -> str:
    chars = string.ascii_uppercase.replace("O", "").replace("I", "") + string.digits.replace("0", "")
    return f"{prefix}-{''.join(secrets.choice(chars) for _ in range(length))}"


def get_effective_plan(user: User, session: Session | None = None) -> str:
    if user.plan != "premium":
        return "free"
    if user.plan_expires_at and user.plan_expires_at < datetime.utcnow():
        user.plan = "free"
        if session is not None:
            session.add(user)
            session.commit()
        return "free"
    return "premium"


class ValidateRequest(BaseModel):
    code: str


class ValidateResponse(BaseModel):
    valid: bool
    plan: str | None = None
    expiresAt: datetime | None = None


@router.post("/validate", response_model=ValidateResponse)
def validate_code(
    body: ValidateRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    code = body.code.strip().upper()
    inv = session.exec(
        select(InvitationCode).where(
            InvitationCode.code == code,
            InvitationCode.is_active == True,  # noqa: E712
        )
    ).first()

    if not inv:
        raise HTTPException(400, "邀请码无效")
    if inv.max_uses is not None and inv.used_count >= inv.max_uses:
        raise HTTPException(400, "邀请码已用完")

    plan_type = inv.plan_type or "premium"
    duration_days = inv.duration_days or 30
    expires_at = datetime.utcnow() + timedelta(days=duration_days)

    user.plan = plan_type
    user.plan_expires_at = expires_at
    session.add(user)

    inv.used_count += 1
    session.add(inv)
    session.commit()

    return ValidateResponse(valid=True, plan=plan_type, expiresAt=expires_at)


class CreateCodeRequest(BaseModel):
    adminKey: str
    planType: str = "premium"
    durationDays: int = 30
    maxUses: int = 1
    prefix: str = "EQ"


@router.post("/admin/create-code")
def create_code(body: CreateCodeRequest, session: Session = Depends(get_session)):
    if not settings.invite_admin_key or body.adminKey != settings.invite_admin_key:
        raise HTTPException(403, "无权限")

    code = _generate_code(body.prefix)
    inv = InvitationCode(
        code=code,
        plan_type=body.planType,
        duration_days=body.durationDays,
        max_uses=body.maxUses,
    )
    session.add(inv)
    session.commit()
    session.refresh(inv)
    return {"ok": True, "code": {"code": inv.code, "planType": inv.plan_type, "durationDays": inv.duration_days}}


@router.get("/admin/codes")
def list_codes(adminKey: str, session: Session = Depends(get_session)):
    if not settings.invite_admin_key or adminKey != settings.invite_admin_key:
        raise HTTPException(403, "无权限")
    codes = session.exec(select(InvitationCode).order_by(InvitationCode.created_at.desc())).all()
    return codes


@router.get("/plan")
def get_plan(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    plan = get_effective_plan(user, session)
    return {"plan": plan, "expiresAt": user.plan_expires_at}


@router.get("/usage")
def get_usage(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    plan = get_effective_plan(user, session)
    if plan == "premium":
        return {"plan": "premium", "limit": 9999, "used": 0, "remaining": 9999}

    today = datetime.utcnow().date()
    from app.models.practice import Practice

    count = len(
        session.exec(
            select(Practice).where(
                Practice.user_id == user.id,
                Practice.completed_at >= datetime.combine(today, datetime.min.time()),
            )
        ).all()
    )
    limit = FREE_DAILY_PRACTICE_LIMIT
    return {"plan": "free", "limit": limit, "used": count, "remaining": max(0, limit - count)}
