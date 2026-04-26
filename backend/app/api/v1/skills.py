"""技能路由 - /api/v1/skills"""

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.core.db import get_session
from app.models.skill import Skill, SkillProgress
from app.models.user import User
from app.services.auth import get_current_user

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("")
def list_skills(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    skills = session.exec(select(Skill)).all()
    progress_map = {
        p.skill_id: p
        for p in session.exec(
            select(SkillProgress).where(SkillProgress.user_id == user.id)
        ).all()
    }
    result = []
    for s in skills:
        p = progress_map.get(s.id)
        result.append({
            "id": s.id,
            "name": s.name,
            "category": s.category,
            "stage": s.stage,
            "description": s.description,
            "level": p.level if p else 0,
            "next_review_at": p.next_review_at.isoformat() if p and p.next_review_at else None,
        })
    return result


@router.get("/{skill_id}")
def get_skill(
    skill_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    skill = session.get(Skill, skill_id)
    if not skill:
        from fastapi import HTTPException
        raise HTTPException(404, "技能不存在")
    progress = session.exec(
        select(SkillProgress)
        .where(SkillProgress.user_id == user.id)
        .where(SkillProgress.skill_id == skill_id)
    ).first()
    return {
        "id": skill.id,
        "name": skill.name,
        "category": skill.category,
        "stage": skill.stage,
        "description": skill.description,
        "patterns": skill.patterns,
        "examples": skill.examples,
        "level": progress.level if progress else 0,
        "correct_streak": progress.correct_streak if progress else 0,
        "next_review_at": progress.next_review_at.isoformat() if progress and progress.next_review_at else None,
    }
