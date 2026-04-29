"""日记诊断服务 - 调用 P5 分析真实场景"""

import json

from sqlmodel import Session

from app.models.skill import Skill
from app.prompts import p5_diary_diagnosis
from app.services.llm import get_async_llm


def _build_skills_json(session: Session) -> str:
    skills = session.exec(__import__("sqlmodel").select(Skill)).all()
    compact = [{"id": s.id, "name": s.name, "description": s.description} for s in skills]
    return json.dumps(compact, ensure_ascii=False)


async def diagnose_diary(
    context: str,
    other_party: str,
    their_words: str,
    my_response: str,
    outcome: str,
    session: Session,
    mode: str = "react",
) -> dict:
    """
    返回诊断结果：
    { identified_skills, diagnosis_brief, socratic_questions,
      rewrite_suggestion_hidden, referenced_style }

    mode="react"：对方说 X，我回 Y → 评估"应对"（默认）
    mode="initiate"：我打算找 X 聊 Y → 评估"开口"
    """
    llm = get_async_llm()
    skills_json = _build_skills_json(session)
    sys_p, usr_p = p5_diary_diagnosis.build(
        context=context,
        other_party=other_party,
        their_words=their_words,
        my_response=my_response,
        outcome=outcome,
        skills_json=skills_json,
        mode=mode,
    )
    result = await llm.chat_json(sys_p, usr_p, temperature=0.5)
    return {
        "identified_skills": result.get("identified_skills", []),
        "diagnosis_brief": result.get("diagnosis_brief", ""),
        "socratic_questions": result.get("socratic_questions", []),
        "rewrite_suggestion_hidden": result.get("rewrite_suggestion_hidden", ""),
        "referenced_style": result.get("referenced_style", "none"),
    }
