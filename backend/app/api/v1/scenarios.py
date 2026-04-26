"""场景库路由 - /api/v1/scenarios

供前端"自由练习"页面展示并挑选具体场景。
"""

import json

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from app.core.db import get_session
from app.models.scenario import ScenarioTemplate
from app.models.skill import Skill
from app.models.user import User
from app.services.auth import get_current_user

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


@router.get("")
def list_scenarios(
    role: str = Query("auto", description="auto=用户当前角色, all=全部, 其它=指定角色"),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """返回场景列表，按 category 分组。auto = 用 user.target_role 过滤"""
    target_role = role
    if role == "auto":
        target_role = user.target_role or "general"

    templates = session.exec(select(ScenarioTemplate)).all()
    skills = {s.id: s for s in session.exec(select(Skill)).all()}

    items: list[dict] = []
    for t in templates:
        try:
            applicable = json.loads(t.applicable_roles)
        except Exception:
            applicable = ["general"]
        if target_role != "all" and target_role not in applicable and "general" not in applicable:
            continue

        try:
            primary_skills = json.loads(t.primary_skills)
        except Exception:
            primary_skills = []

        skill_tags = []
        for sid in primary_skills[:3]:
            s = skills.get(sid)
            if s:
                skill_tags.append({"id": sid, "name": s.name, "icon": s.icon or "✦"})

        items.append({
            "id": t.id,
            "category": t.category,
            "sub_type": t.sub_type,
            "title": t.title,
            "role_brief": t.role_brief,
            "tension_brief": t.tension_brief,
            "user_goal_brief": t.user_goal_brief,
            "difficulty": t.difficulty,
            "applicable_roles": applicable,
            "primary_skill_id": primary_skills[0] if primary_skills else None,
            "skills": skill_tags,
        })

    return {
        "role": target_role,
        "total": len(items),
        "items": items,
    }
