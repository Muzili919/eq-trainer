"""苏格拉底引导服务 - 调用 P4，评分 < 60 时触发"""

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
    total_score: float = 50,
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
        total_score=total_score,
    )
    result = await llm.chat_json(sys_p, usr_p, temperature=0.6)
    question = result.get("question", "").strip()
    if not question:
        return None
    return {
        "question": question,
        "encouragement": result.get("encouragement", ""),
    }


async def coach_followup(
    skill_name: str,
    socratic_question: str,
    user_reflection: str,
) -> str:
    """用户回答了教练问题后，给一句温和的引导，把人带回场景。

    返回教练的一句回复。
    """
    llm = get_async_llm()
    sys_p = (
        "你是高情商教练，正在帮用户做沟通练习的反思环节。"
        "用户刚回答了你提的问题。你要：\n"
        "1. 肯定 ta 的思考（哪怕只有一点点到位）\n"
        "2. 用一句温和的话把 ta 引回场景——鼓励 ta 重新回应对方\n"
        "3. 口语化，1-2 句话，不要太长\n"
        "直接输出纯文本，不要 JSON，不要解释。"
    )
    usr_p = (
        f"技能：【{skill_name}】\n"
        f"你问的问题：{socratic_question}\n"
        f"用户的回答：{user_reflection}\n\n"
        "给 ta 一句回复，把 ta 引回场景。"
    )
    try:
        text = await llm.chat_text(sys_p, usr_p, temperature=0.7)
        text = (text or "").strip()
        return text or "想得不错。那换个方式，重新回应对方试试？"
    except Exception:
        return "想得不错。那换个方式，重新回应对方试试？"
