"""首页聚合路由 - /api/v1/home

一个端点把首页所有数据打包返回，避免前端瀑布请求。
"""

from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.core.db import get_session
from app.models.practice import Practice, PracticeTurn
from app.models.scenario import ScenarioTemplate
from app.models.skill import Skill, SkillProgress
from app.models.streak import DailyLog, DailyStreak
from app.models.user import User
from app.services.auth import get_current_user

router = APIRouter(prefix="/home", tags=["home"])

WEEKDAY_LABELS = ["一", "二", "三", "四", "五", "六", "日"]
STYLE_NAMES = {
    "huangbo": "黄渤",
    "xuzhisheng": "徐志胜",
    "lixueqin": "李雪琴",
    "hejiong": "何炅",
}


def _build_streak_block(user_id: int, session: Session) -> dict:
    streak = session.exec(
        select(DailyStreak).where(DailyStreak.user_id == user_id)
    ).first()
    current = streak.current_streak if streak else 0

    today = date.today()
    week_start = today - timedelta(days=6)
    logs = session.exec(
        select(DailyLog)
        .where(DailyLog.user_id == user_id)
        .where(DailyLog.log_date >= week_start)
    ).all()
    log_map = {l.log_date: l for l in logs}

    week = []
    week_done = 0
    for i in range(7):
        d = week_start + timedelta(days=i)
        log = log_map.get(d)
        done = bool(log and ((log.practices_completed or 0) > 0 or (log.diary_count or 0) > 0))
        if done:
            week_done += 1
        week.append({
            "date": d.isoformat(),
            "day": d.day,
            "weekday": WEEKDAY_LABELS[d.weekday()],
            "done": done,
            "today": d == today,
        })

    return {
        "current": current,
        "day_count": current,
        "week": week,
        "week_done": week_done,
    }


def _build_style_stats(user: User, session: Session) -> dict:
    """风格分布

    当前 schema 只记录了 score_style_match（与 user.target_style 的相似度），
    无法精确还原四风格分布。这里用一个折中方案：
    - 主风格（target_style 或默认 huangbo）= 基础占比 + score_style_match 加成
    - 其他三个风格按递减分配剩余
    - total_count 用真实评分次数
    新用户（无评分）返回全 0，前端显示空态文案。
    """
    turns = session.exec(
        select(PracticeTurn)
        .join(Practice, Practice.id == PracticeTurn.practice_id)  # type: ignore
        .where(Practice.user_id == user.id)
        .where(PracticeTurn.total_score.isnot(None))  # type: ignore
    ).all()

    total_count = len(turns)
    target = user.target_style or "huangbo"
    if target not in STYLE_NAMES:
        target = "huangbo"

    others = [k for k in STYLE_NAMES if k != target]

    if total_count == 0:
        distribution = [{"key": target, "name": STYLE_NAMES[target], "pct": 0}]
        for k in others:
            distribution.append({"key": k, "name": STYLE_NAMES[k], "pct": 0})
        return {"total_count": 0, "distribution": distribution, "top_recent": None}

    avg_match = sum((t.score_style_match or 0) for t in turns) / total_count
    main_pct = round(45 + avg_match * 0.3)
    main_pct = max(40, min(72, main_pct))
    rest = 100 - main_pct
    other_pcts = [round(rest * 0.55), round(rest * 0.30), max(0, rest - round(rest * 0.55) - round(rest * 0.30))]

    distribution = [{"key": target, "name": STYLE_NAMES[target], "pct": main_pct}]
    for k, p in zip(others, other_pcts):
        distribution.append({"key": k, "name": STYLE_NAMES[k], "pct": p})

    # top_recent：最近 7 天 score_style_match 最高时取的 target_style
    recent_cutoff = datetime.utcnow() - timedelta(days=7)
    recent_turns = [t for t in turns if t.created_at >= recent_cutoff]
    top_recent = target if recent_turns else None

    return {
        "total_count": total_count,
        "distribution": distribution,
        "top_recent": top_recent,
    }


def _build_highlight(user_id: int, session: Session) -> dict | None:
    cutoff = datetime.utcnow() - timedelta(days=7)
    rows = session.exec(
        select(PracticeTurn)
        .join(Practice, Practice.id == PracticeTurn.practice_id)  # type: ignore
        .where(Practice.user_id == user_id)
        .where(PracticeTurn.total_score.isnot(None))  # type: ignore
        .where(PracticeTurn.created_at >= cutoff)
        .where(PracticeTurn.user_input != "")
        .order_by(PracticeTurn.total_score.desc())  # type: ignore
        .limit(1)
    ).all()
    if not rows:
        return None
    turn = rows[0]
    prev = session.exec(
        select(PracticeTurn)
        .where(PracticeTurn.practice_id == turn.practice_id)
        .where(PracticeTurn.turn_number == turn.turn_number - 1)
    ).first()
    their_words = (prev.ai_message if prev else None) or ""

    scores = {}
    if turn.score_decency is not None:
        scores["decency"] = round(turn.score_decency)
    if turn.score_defusion is not None:
        scores["defusion"] = round(turn.score_defusion)
    if turn.score_humor is not None:
        scores["humor"] = round(turn.score_humor)
    if turn.score_style_match is not None:
        scores["style_match"] = round(turn.score_style_match)

    practice = session.get(Practice, turn.practice_id)
    user = session.get(User, user_id)
    top_style = (user.target_style if user else None) or "huangbo"

    return {
        "their_words": their_words,
        "my_response": turn.user_input,
        "scores": scores,
        "top_style": top_style,
        "top_style_name": STYLE_NAMES.get(top_style, "黄渤"),
        "scenario_title": practice.scenario_title if practice else None,
    }


def _build_blind_box(user_id: int, session: Session) -> dict:
    """今日盲盒：3 道场景题

    优先级：
    1. SRS 到期且 level<5 的技能（next_review_at <= now，按 next_review_at asc）
    2. 不够 3 个就用 level<5 的技能按 level asc 补
    3. 都不够就用 sort_order asc 取
    """
    skills = session.exec(select(Skill).order_by(Skill.sort_order)).all()
    skill_map = {s.id: s for s in skills}

    progress_list = session.exec(
        select(SkillProgress).where(SkillProgress.user_id == user_id)
    ).all()
    progress_map = {p.skill_id: p for p in progress_list}

    now = datetime.utcnow()
    due = [p for p in progress_list if p.level < 5 and p.next_review_at and p.next_review_at <= now]
    due.sort(key=lambda p: p.next_review_at or now)

    chosen_ids: list[str] = []
    for p in due:
        if p.skill_id in skill_map and len(chosen_ids) < 3:
            chosen_ids.append(p.skill_id)

    if len(chosen_ids) < 3:
        weak = sorted(progress_list, key=lambda p: p.level)
        for p in weak:
            if p.level < 5 and p.skill_id not in chosen_ids and p.skill_id in skill_map:
                chosen_ids.append(p.skill_id)
                if len(chosen_ids) >= 3:
                    break

    if len(chosen_ids) < 3:
        for s in skills:
            if s.id not in chosen_ids:
                chosen_ids.append(s.id)
                if len(chosen_ids) >= 3:
                    break

    # 为每个 skill 找一个匹配的 ScenarioTemplate（primary_skills JSON 里包含此 skill_id）
    # 优先返回与 user.target_role 匹配的场景，兜底 general
    import json as _json

    user_obj = session.get(__import__("app.models.user", fromlist=["User"]).User, user_id)
    user_role = (user_obj.target_role if user_obj else None) or "general"

    templates = session.exec(select(ScenarioTemplate)).all()

    def _find_template(skill_id: str) -> ScenarioTemplate | None:
        role_matched = None
        fallback = None
        for t in templates:
            try:
                ps = _json.loads(t.primary_skills)
            except Exception:
                ps = []
            if skill_id not in ps:
                continue
            try:
                roles = _json.loads(t.applicable_roles)
            except Exception:
                roles = ["general"]
            if user_role in roles:
                return t  # 精确角色匹配，直接返回
            if "general" in roles and fallback is None:
                fallback = t  # general 场景作为 fallback
        return fallback

    scenes = []
    for sid in chosen_ids[:3]:
        s = skill_map[sid]
        p = progress_map.get(sid)
        tpl = _find_template(sid)
        scenes.append({
            "skill_id": s.id,
            "skill_name": s.name,
            "icon": s.icon or "✦",
            "stage": s.stage,
            "level": p.level if p else 0,
            "scene_brief": s.description,
            "scenario_title": tpl.title if tpl else None,
            "scenario_setup": tpl.role_brief if tpl else None,
            "tension_brief": tpl.tension_brief if tpl else None,
            "difficulty": tpl.difficulty if tpl else 3,
            "category": tpl.category if tpl else None,
        })

    skills_label = "、".join([f"「{sc['skill_name']} {sc['skill_id']}」" for sc in scenes])

    return {
        "scenes": scenes,
        "skills_label": skills_label,
        "total": len(scenes),
        "minutes_estimate": 10,
    }


def _build_skills_overview(user_id: int, session: Session) -> dict:
    skills = session.exec(select(Skill).order_by(Skill.sort_order)).all()
    progress_map = {
        p.skill_id: p
        for p in session.exec(
            select(SkillProgress).where(SkillProgress.user_id == user_id)
        ).all()
    }
    items = []
    lit = 0
    for s in skills:
        p = progress_map.get(s.id)
        level = p.level if p else 0
        if level >= 1:
            lit += 1
        items.append({
            "id": s.id,
            "name": s.name,
            "icon": s.icon or "✦",
            "stage": s.stage,
            "level": level,
        })
    return {
        "total": len(skills),
        "lit": lit,
        "items": items,
    }


@router.get("/summary")
def home_summary(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return {
        "username": user.username,
        "today": date.today().isoformat(),
        "streak": _build_streak_block(user.id, session),
        "style_stats": _build_style_stats(user, session),
        "highlight": _build_highlight(user.id, session),
        "today_blind_box": _build_blind_box(user.id, session),
        "skills": _build_skills_overview(user.id, session),
    }
