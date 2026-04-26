"""苏格拉底引导服务 - 调用 P4，评分 < 70 时触发"""

from app.prompts import p4_socratic
from app.services.llm import get_async_llm

MAX_ATTEMPTS = 3


async def get_guiding_question(
    skill_name: str,
    context: str,
    user_response: str,
    ai_feedback: str,
    used_questions: list[str],
    socratic_attempts: int,
) -> dict | None:
    """
    还有机会时返回引导问题 { question, encouragement }
    超过 MAX_ATTEMPTS 返回 None（调用方直接展示改写示范）
    """
    if socratic_attempts >= MAX_ATTEMPTS:
        return None

    llm = get_async_llm()
    used_str = "\n".join(f"- {q}" for q in used_questions) if used_questions else "（无）"
    sys_p, usr_p = p4_socratic.build(
        skill_name=skill_name,
        context=context,
        user_response=user_response,
        ai_feedback=ai_feedback,
        used_questions=used_str,
    )
    result = await llm.chat_json(sys_p, usr_p, temperature=0.6)
    return {
        "question": result.get("question", ""),
        "encouragement": result.get("encouragement", ""),
    }
