"""练习路由 - /api/v1/practice

流程：
  POST /start   → 生成场景，返回 practice_id + 首句话
  POST /{id}/turn → 用户发一句，返回 AI 回应 + 评分
  POST /{id}/complete → 结束练习，更新 SRS
"""

import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.db import get_session
from app.models.diary import Diary, DiaryAnalysis
from app.models.practice import Practice, PracticeTurn
from app.models.scenario import ScenarioTemplate
from app.models.skill import Skill, SkillProgress
from app.models.style import StyleReference
from app.models.user import User
from app.services.auth import get_current_user
from app.services.roleplay import get_ai_reply
from app.services.scenario_gen import generate_scenario, render_template_opening
from app.services.scoring import score_response
from app.services.socratic import get_guiding_question

router = APIRouter(prefix="/practice", tags=["practice"])

SCORE_THRESHOLD_SOCRATIC = 70
SCORE_THRESHOLD_DIRECT = 50


def _get_skill_or_404(skill_id: str, session: Session) -> Skill:
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(404, f"技能 {skill_id} 不存在")
    return skill


def _build_style_references(user: User, session: Session) -> str:
    refs = session.exec(
        select(StyleReference)
        .where(StyleReference.persona == user.target_style)
        .limit(7)
    ).all()
    if not refs:
        refs = session.exec(select(StyleReference).limit(10)).all()
    lines = []
    for r in refs:
        lines.append(f"[{r.persona}] 场景：{r.trigger}\n回应：{r.response}")
    return "\n\n".join(lines)


def _build_skills_compact(session: Session) -> str:
    skills = session.exec(select(Skill)).all()
    lines = [f"{s.id}：{s.name} — {s.description}" for s in skills]
    return "\n".join(lines)


def _build_dialog_history(turns: list[PracticeTurn]) -> str:
    lines = []
    for t in turns:
        if t.ai_message:
            lines.append(f"对方：{t.ai_message}")
        lines.append(f"你：{t.user_input}")
    return "\n".join(lines)


class StartRequest(BaseModel):
    skill_id: str
    difficulty: int = 3
    scenario_template_id: int | None = None
    diary_id: int | None = None


class StartResponse(BaseModel):
    practice_id: int
    title: str
    scenario_setup: str
    initial_message: str
    ai_emotion: str


@router.post("/start", response_model=StartResponse)
async def start_practice(
    body: StartRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    template: ScenarioTemplate | None = None
    diary: Diary | None = None

    if body.diary_id:
        diary = session.get(Diary, body.diary_id)
        if not diary or diary.user_id != user.id:
            raise HTTPException(404, "日记不存在")
        analysis = session.exec(
            select(DiaryAnalysis).where(DiaryAnalysis.diary_id == body.diary_id)
        ).first()
        if analysis:
            try:
                identified = json.loads(analysis.identified_skills)
            except Exception:
                identified = []
            if identified:
                body.skill_id = identified[0]
    elif body.scenario_template_id:
        template = session.get(ScenarioTemplate, body.scenario_template_id)
        if not template:
            raise HTTPException(404, "场景模板不存在")
        try:
            primary_skills = json.loads(template.primary_skills)
        except Exception:
            primary_skills = []
        if primary_skills:
            body.skill_id = primary_skills[0]

    skill = _get_skill_or_404(body.skill_id, session)

    if diary:
        analysis = session.exec(
            select(DiaryAnalysis).where(DiaryAnalysis.diary_id == body.diary_id)
        ).first()
        diagnosis = analysis.diagnosis_brief if analysis else ""
        scenario = {
            "title": f"真实场景：{diary.other_party or '对方'}",
            "scenario_setup": f"{diary.context}\n\n{diagnosis}".strip(),
            "role_brief": diary.other_party or "对方",
            "initial_message": diary.their_words,
            "ai_emotion": "annoyed",
            "category": "diary",
        }
    elif template:
        opening = await render_template_opening(template)
        scenario = {
            "title": template.title,
            "scenario_setup": template.role_brief,
            "role_brief": template.role_brief,
            "initial_message": opening["initial_message"],
            "ai_emotion": opening["ai_emotion"],
            "category": template.category,
        }
    else:
        scenario = await generate_scenario(
            skill_name=skill.name,
            skill_description=skill.description,
            skill_patterns=skill.patterns or "",
            difficulty=body.difficulty,
            user_style_preference=user.target_style or "none",
            user_target_style=user.target_style or "none",
            recent_avg_score=0.0,
            used_categories=[],
        )
    practice = Practice(
        user_id=user.id,
        skill_id=skill.id,
        scenario_title=scenario["title"],
        scenario_setup=scenario["scenario_setup"],
        role_brief=scenario["role_brief"],
        difficulty=body.difficulty,
    )
    session.add(practice)
    session.commit()
    session.refresh(practice)

    # 记录 AI 开场白作为第 0 轮（只有 ai_message）
    turn0 = PracticeTurn(
        practice_id=practice.id,
        turn_number=0,
        user_input="",
        ai_message=scenario["initial_message"],
        ai_emotion=scenario["ai_emotion"],
    )
    session.add(turn0)
    session.commit()

    return StartResponse(
        practice_id=practice.id,
        title=scenario["title"],
        scenario_setup=scenario["scenario_setup"],
        initial_message=scenario["initial_message"],
        ai_emotion=scenario["ai_emotion"],
    )


class TurnRequest(BaseModel):
    user_input: str
    input_mode: str = "text"  # text | voice


class TurnResponse(BaseModel):
    turn_number: int
    ai_message: str
    ai_emotion: str
    should_end: bool
    total_score: float
    scores: dict
    narrative: str
    strengths: str
    improvements: str
    rewrite_suggestion: str | None
    socratic_question: str | None
    socratic_encouragement: str | None
    well_used: list[str]
    missing: list[str]


@router.post("/{practice_id}/turn", response_model=TurnResponse)
async def submit_turn(
    practice_id: int,
    body: TurnRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    practice = session.get(Practice, practice_id)
    if not practice or practice.user_id != user.id:
        raise HTTPException(404, "练习不存在")
    if practice.completed_at:
        raise HTTPException(400, "该练习已结束")

    turns = session.exec(
        select(PracticeTurn)
        .where(PracticeTurn.practice_id == practice_id)
        .order_by(PracticeTurn.turn_number)
    ).all()
    turn_number = len([t for t in turns if t.user_input]) + 1
    dialog_history = _build_dialog_history([t for t in turns if t.user_input])
    their_words = turns[-1].ai_message if turns else ""

    style_references = _build_style_references(user, session)
    skills_compact = _build_skills_compact(session)

    skill = session.get(Skill, practice.skill_id)
    scoring_result, ai_reply = await __import__("asyncio").gather(
        score_response(
            scenario_setup=practice.scenario_setup or "",
            dialog_history=dialog_history,
            user_response=body.user_input,
            target_skill=f"{skill.name}：{skill.description}" if skill else "",
            style_references=style_references,
            their_words=their_words,
            skills_compact_list=skills_compact,
            humor_weight=user.humor_weight or 0.30,
        ),
        get_ai_reply(
            role_brief=practice.role_brief or "",
            scenario_setup=practice.scenario_setup or "",
            dialog_history=dialog_history,
            user_response=body.user_input,
            turn_number=turn_number,
        ),
    )

    total_score = scoring_result["total_score"]
    socratic_result = None
    used_questions = [t.socratic_question for t in turns if t.socratic_question]
    socratic_attempts = sum(1 for t in turns if t.socratic_attempts)

    if SCORE_THRESHOLD_DIRECT <= total_score < SCORE_THRESHOLD_SOCRATIC:
        socratic_result = await get_guiding_question(
            skill_name=skill.name if skill else "",
            context=f"{practice.scenario_setup}\n\n{dialog_history}",
            user_response=body.user_input,
            ai_feedback=scoring_result.get("improvements", ""),
            used_questions=used_questions,
            socratic_attempts=socratic_attempts,
        )

    new_turn = PracticeTurn(
        practice_id=practice_id,
        turn_number=turn_number,
        user_input=body.user_input,
        user_input_mode=body.input_mode,
        ai_message=ai_reply["message"],
        ai_emotion=ai_reply["emotion"],
        score_decency=scoring_result.get("scores", {}).get("decency"),
        score_defusion=scoring_result.get("scores", {}).get("defusion"),
        score_humor=scoring_result.get("scores", {}).get("humor"),
        score_style_match=scoring_result.get("scores", {}).get("style_match"),
        total_score=total_score,
        strengths=scoring_result.get("strengths"),
        improvements=scoring_result.get("improvements"),
        rewrite_suggestion=scoring_result.get("rewrite_suggestion"),
        socratic_question=socratic_result["question"] if socratic_result else None,
        socratic_attempts=(socratic_attempts + 1) if socratic_result else socratic_attempts,
        well_used_skills=json.dumps(scoring_result.get("well_used", []), ensure_ascii=False),
        missing_skills=json.dumps(scoring_result.get("missing", []), ensure_ascii=False),
    )
    session.add(new_turn)
    session.commit()

    return TurnResponse(
        turn_number=turn_number,
        ai_message=ai_reply["message"],
        ai_emotion=ai_reply["emotion"],
        should_end=ai_reply["should_end"],
        total_score=total_score,
        scores=scoring_result.get("scores", {}),
        narrative=scoring_result.get("narrative", ""),
        strengths=scoring_result.get("strengths", ""),
        improvements=scoring_result.get("improvements", ""),
        rewrite_suggestion=scoring_result.get("rewrite_suggestion"),
        socratic_question=socratic_result["question"] if socratic_result else None,
        socratic_encouragement=socratic_result["encouragement"] if socratic_result else None,
        well_used=scoring_result.get("well_used", []),
        missing=scoring_result.get("missing", []),
    )


@router.post("/{practice_id}/complete")
async def complete_practice(
    practice_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    practice = session.get(Practice, practice_id)
    if not practice or practice.user_id != user.id:
        raise HTTPException(404, "练习不存在")

    turns = session.exec(
        select(PracticeTurn)
        .where(PracticeTurn.practice_id == practice_id)
        .where(PracticeTurn.total_score.isnot(None))  # type: ignore
    ).all()

    if turns:
        avg = sum(t.total_score for t in turns if t.total_score) / len(turns)
        practice.avg_score = avg
    practice.completed_at = datetime.utcnow()
    session.add(practice)

    # 更新 SRS
    progress = session.exec(
        select(SkillProgress)
        .where(SkillProgress.user_id == user.id)
        .where(SkillProgress.skill_id == practice.skill_id)
    ).first()
    if not progress:
        progress = SkillProgress(user_id=user.id, skill_id=practice.skill_id)
        session.add(progress)

    avg_score = practice.avg_score or 0
    if avg_score >= 75:
        progress.correct_streak = (progress.correct_streak or 0) + 1
        if progress.correct_streak >= 3:
            progress.level = min(5, (progress.level or 0) + 1)
            progress.correct_streak = 0
    else:
        progress.correct_streak = 0
        progress.level = max(0, (progress.level or 0) - 1)

    session.commit()
    return {"ok": True, "avg_score": practice.avg_score, "skill_level": progress.level}
