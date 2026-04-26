"""场景生成服务 - 调用 P1 生成每日训练场景"""

from app.prompts import p1_scenario_gen
from app.services.llm import get_async_llm


async def generate_scenario(
    skill_name: str,
    skill_description: str,
    skill_patterns: str,
    difficulty: int,
    user_style_preference: str,
    user_target_style: str,
    recent_avg_score: float,
    used_categories: list[str],
) -> dict:
    """
    返回生成的场景：
    { title, scenario_setup, role_brief, initial_message, ai_emotion, category }
    """
    llm = get_async_llm()
    used_str = "、".join(used_categories) if used_categories else "无"
    sys_p, usr_p = p1_scenario_gen.build(
        skill_name=skill_name,
        skill_description=skill_description,
        skill_patterns=skill_patterns,
        difficulty=max(1, min(5, difficulty)),
        user_style_preference=user_style_preference,
        user_target_style=user_target_style,
        recent_avg_score=recent_avg_score,
        used_categories=used_str,
    )
    result = await llm.chat_json(sys_p, usr_p, temperature=0.9)
    return {
        "title": result.get("title", ""),
        "scenario_setup": result.get("scenario_setup", ""),
        "role_brief": result.get("role_brief", ""),
        "initial_message": result.get("initial_message", ""),
        "ai_emotion": result.get("ai_emotion", "neutral"),
        "category": result.get("category", "stranger"),
    }
