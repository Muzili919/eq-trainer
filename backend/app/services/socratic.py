"""苏格拉底引导服务 - 调用 P4，评分 < 60 时触发，多轮闭环"""

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
    techniques_used: list[str] | None = None,
    techniques_available: list[str] | None = None,
) -> dict | None:
    """
    还有机会时返回引导问题 { question, encouragement }
    超过 MAX_ATTEMPTS 返回 None
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
        techniques_used=techniques_used,
        techniques_available=techniques_available,
    )
    result = await llm.chat_json(sys_p, usr_p, temperature=0.6)
    question = result.get("question", "").strip()
    if not question:
        return None
    return {
        "question": question,
        "encouragement": result.get("encouragement", ""),
    }


async def coach_reflect(
    skill_name: str,
    socratic_question: str,
    user_reflection: str,
    round_number: int,
    techniques_used: list[str] | None = None,
) -> dict:
    """用户回答了教练问题后，判断理解程度并给出反馈。

    返回：
    {
        "coach_reply": "教练回复",
        "is_complete": True/False,  # True=理解到位可以结束
        "technique_hint": "可选的手法提示"
    }
    """
    llm = get_async_llm()
    round_hint = ""
    if round_number >= MAX_ATTEMPTS - 1:
        round_hint = "这是最后一轮引导，必须温和收尾，给一个明确的提示或方向。"
    elif round_number == 1:
        round_hint = "这是第一次回答，判断理解程度：到位就鼓励收尾，不到位就追问更具体的角度。"
    else:
        round_hint = "继续引导，可以换个角度或者给更多提示。"

    tech_context = ""
    if techniques_used:
        tech_context = f"学生之前用过的手法：{'、'.join(techniques_used)}"

    sys_p = (
        "你是高情商教练，正在帮用户做沟通练习的反思环节。\n"
        "用户刚回答了你提的问题。你要：\n"
        "1. 判断用户的理解程度：到位 / 部分到位 / 没到位\n"
        "2. 到位 → 肯定 + 鼓励回场景（is_complete=true）\n"
        "3. 部分到位 → 肯定对的部分 + 追问更深（is_complete=false）\n"
        "4. 没到位 → 不批评，换个角度引导或给提示（is_complete=false）\n"
        f"5. {round_hint}\n"
        "6. 口语化，1-3 句话\n"
        "直接输出 JSON。"
    )
    usr_p = (
        f"技能：【{skill_name}】\n"
        f"你问的问题：{socratic_question}\n"
        f"用户的回答：{user_reflection}\n"
        f"第 {round_number} 轮（最多 {MAX_ATTEMPTS} 轮）\n"
        f"{tech_context}\n\n"
        "给 ta 回复。"
    )
    try:
        result = await llm.chat_json(sys_p, usr_p, temperature=0.7)
        reply = (result.get("coach_reply") or "").strip()
        if not reply:
            # fallback to text mode if JSON parsing failed
            text = await llm.chat_text(
                "你是高情商教练。用户回答了你的反思问题。给一句温和的回复，把 ta 引回场景。口语化1-2句话。直接输出文本。",
                f"你的问题：{socratic_question}\n用户回答：{user_reflection}",
                temperature=0.7,
            )
            reply = (text or "").strip() or "想得不错，那换个方式重新回应对方试试？"

        return {
            "coach_reply": reply,
            "is_complete": bool(result.get("is_complete", round_number >= MAX_ATTEMPTS)),
            "technique_hint": result.get("technique_hint"),
        }
    except Exception:
        return {
            "coach_reply": "想得不错，那换个方式重新回应对方试试？",
            "is_complete": True,
            "technique_hint": None,
        }


# Backward compatibility wrapper
async def coach_followup(
    skill_name: str,
    socratic_question: str,
    user_reflection: str,
) -> str:
    """旧接口兼容 — 返回纯文本教练回复"""
    result = await coach_reflect(
        skill_name=skill_name,
        socratic_question=socratic_question,
        user_reflection=user_reflection,
        round_number=1,
    )
    return result["coach_reply"]
