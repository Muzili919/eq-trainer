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
from app.services.socratic import get_guiding_question, coach_reflect, coach_followup
from app.services.streak import touch_daily_log

router = APIRouter(prefix="/practice", tags=["practice"])

SCORE_THRESHOLD_SOCRATIC = 60


def _get_skill_or_404(skill_id: str, session: Session) -> Skill:
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(404, f"技能 {skill_id} 不存在")
    return skill


def _build_style_references(user: User, session: Session) -> str:
    try:
        user_styles = json.loads(user.target_styles) if user.target_styles else []
    except Exception:
        user_styles = []
    if not user_styles:
        user_styles = [user.target_style] if user.target_style else ["huangbo"]
    refs = session.exec(
        select(StyleReference)
        .where(StyleReference.persona.in_(user_styles))
        .limit(10)
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
        if t.turn_type == "reflection":
            continue
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
    # Plan 过期检查
    from app.api.v1.invite import get_effective_plan, FREE_DAILY_PRACTICE_LIMIT
    plan = get_effective_plan(user, session)
    if plan != "premium":
        today = datetime.utcnow().date()
        today_count = len(
            session.exec(
                select(Practice).where(
                    Practice.user_id == user.id,
                    Practice.completed_at >= datetime.combine(today, datetime.min.time()),
                )
            ).all()
        )
        if today_count >= FREE_DAILY_PRACTICE_LIMIT:
            raise HTTPException(
                429,
                f"今日练习次数已达上限（{today_count}/{FREE_DAILY_PRACTICE_LIMIT}），升级 Premium 可无限练习",
            )

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
        # initiate 模式（我开口）：对方还没说话，给一个等待的开场提示
        # react 模式（旧）：对方说了 their_words 我回应
        if diary.mode == "initiate":
            opener = f"（{diary.other_party or '对方'}抬头看了你一眼，等你开口）"
            initial_emotion = "neutral"
        else:
            opener = diary.their_words or "（你好）"
            initial_emotion = "annoyed"
        # 构建 role_brief：从日记信息推断对方的立场和诉求
        other_name = diary.other_party or "对方"
        if diary.mode == "initiate":
            # 我主动开口 → 对方是被动的，但有自己的态度
            role_brief = (
                f"你是{other_name}。{diary.context} "
                f"此刻{other_name}正在面对你，你不知道对方要说什么，"
                f"但你有自己的立场和顾虑。你是真实的人，有自己的想法，不会被轻易说服。"
            )
        else:
            # 对方先说 → 对方有明确的诉求/态度
            role_brief = (
                f"你是{other_name}。{diary.context} "
                f"你说了「{diary.their_words}」，这说明你有明确的态度和诉求。"
                f"你需要坚持自己的立场，不会因为对方一两句话就轻易改变想法。"
            )
        scenario = {
            "title": f"真实场景：{other_name}",
            "scenario_setup": f"{diary.context}\n\n{diagnosis}".strip(),
            "role_brief": role_brief,
            "initial_message": opener,
            "ai_emotion": initial_emotion,
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
    mode: str = "dialogue"  # dialogue | reflection
    socratic_question: str | None = None  # reflection 模式必传，记录正在回答的教练问题


class TurnResponse(BaseModel):
    turn_number: int
    ai_message: str | None
    ai_emotion: str | None
    should_end: bool
    total_score: float | None
    scores: dict | None
    narrative: str | None
    strengths: str | None
    improvements: str | None
    rewrite_suggestion: str | None
    rewrite_suggestions: list[dict] = []
    techniques_used: list[str] = []
    techniques_available: list[str] = []
    style_matched: str | None = None
    socratic_question: str | None
    socratic_encouragement: str | None
    coach_followup: str | None
    ai_fallback: bool = False
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

    skill = session.get(Skill, practice.skill_id)

    # ── reflection 模式：教练追问，不调 AI 角色，不评分 ──
    if body.mode == "reflection":
        if not (body.socratic_question or "").strip():
            raise HTTPException(400, "reflection 模式必须带 socratic_question")
        followup = await coach_followup(
            skill_name=skill.name if skill else "",
            socratic_question=body.socratic_question,
            user_reflection=body.user_input,
        )
        new_turn = PracticeTurn(
            practice_id=practice_id,
            turn_number=turn_number,
            turn_type="reflection",
            user_input=body.user_input,
            user_input_mode=body.input_mode,
            coach_followup=followup,
            socratic_question=body.socratic_question,
        )
        session.add(new_turn)
        session.commit()

        # 反思也是练习活动，更新打卡（不算练习数，只更新连击日期）
        touch_daily_log(user.id, session)

        return TurnResponse(
            turn_number=turn_number,
            ai_message=None,
            ai_emotion=None,
            should_end=False,
            total_score=None,
            scores=None,
            narrative=None,
            strengths=None,
            improvements=None,
            rewrite_suggestion=None,
            rewrite_suggestions=[],
            techniques_used=[],
            techniques_available=[],
            style_matched=None,
            socratic_question=None,
            socratic_encouragement=None,
            coach_followup=followup,
            well_used=[],
            missing=[],
        )

    # ── dialogue 模式：评分 + AI 角色回话 ──
    dialog_history = _build_dialog_history([t for t in turns if t.user_input])
    their_words = turns[-1].ai_message if turns else ""

    style_references = _build_style_references(user, session)
    skills_compact = _build_skills_compact(session)

    # 获取用户选择的风格路线
    try:
        user_styles = json.loads(user.target_styles) if user.target_styles else []
    except Exception:
        user_styles = [user.target_style] if user.target_style else ["huangbo"]

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
            target_styles=user_styles,
            turn_number=turn_number,
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

    if total_score < SCORE_THRESHOLD_SOCRATIC:
        socratic_result = await get_guiding_question(
            skill_name=skill.name if skill else "",
            context=f"{practice.scenario_setup}\n\n{dialog_history}",
            user_response=body.user_input,
            ai_feedback=scoring_result.get("improvements", ""),
            used_questions=used_questions,
            socratic_attempts=socratic_attempts,
            total_score=total_score,
            techniques_used=scoring_result.get("techniques_used", []),
            techniques_available=scoring_result.get("techniques_available", []),
        )

    new_turn = PracticeTurn(
        practice_id=practice_id,
        turn_number=turn_number,
        turn_type="dialogue",
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

    # dialogue turn 触发活跃连击（不加 practice 计数，那个由 complete 加）
    touch_daily_log(user.id, session)

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
        rewrite_suggestions=scoring_result.get("rewrite_suggestions", []),
        techniques_used=scoring_result.get("techniques_used", []),
        techniques_available=scoring_result.get("techniques_available", []),
        style_matched=scoring_result.get("style_matched"),
        socratic_question=socratic_result["question"] if socratic_result else None,
        socratic_encouragement=socratic_result["encouragement"] if socratic_result else None,
        coach_followup=None,
        ai_fallback=bool(ai_reply.get("fallback")),
        well_used=scoring_result.get("well_used", []),
        missing=scoring_result.get("missing", []),
    )


class ReflectRequest(BaseModel):
    user_reflection: str
    socratic_question: str
    round_number: int = 1


class ReflectResponse(BaseModel):
    coach_reply: str
    is_complete: bool
    technique_hint: str | None = None


@router.post("/{practice_id}/reflect", response_model=ReflectResponse)
async def reflect_turn(
    practice_id: int,
    body: ReflectRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """苏格拉底反思接口 — 评分面板内多轮追问"""
    practice = session.get(Practice, practice_id)
    if not practice or practice.user_id != user.id:
        raise HTTPException(404, "练习不存在")

    skill = session.get(Skill, practice.skill_id)
    turns = session.exec(
        select(PracticeTurn)
        .where(PracticeTurn.practice_id == practice_id)
        .order_by(PracticeTurn.turn_number)
    ).all()

    # 获取上一轮的 techniques（如果有）
    last_scored = None
    for t in reversed(turns):
        if t.total_score is not None:
            last_scored = t
            break

    techniques_used = []
    if last_scored and last_scored.well_used_skills:
        try:
            techniques_used = json.loads(last_scored.well_used_skills)
        except Exception:
            pass

    result = await coach_reflect(
        skill_name=skill.name if skill else "",
        socratic_question=body.socratic_question,
        user_reflection=body.user_reflection,
        round_number=body.round_number,
        techniques_used=techniques_used,
    )

    # 记录反思 turn
    turn_number = len([t for t in turns if t.user_input]) + 1
    new_turn = PracticeTurn(
        practice_id=practice_id,
        turn_number=turn_number,
        turn_type="reflection",
        user_input=body.user_reflection,
        user_input_mode="text",
        coach_followup=result["coach_reply"],
        socratic_question=body.socratic_question,
    )
    session.add(new_turn)
    session.commit()

    return ReflectResponse(**result)


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

    # 完成一次练习 → 打卡 + 累计平均分
    touch_daily_log(user.id, session, practice_completed=True, score=practice.avg_score)

    return {"ok": True, "avg_score": practice.avg_score, "skill_level": progress.level}
