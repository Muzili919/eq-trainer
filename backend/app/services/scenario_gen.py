"""场景生成服务 - 调用 P1 生成每日训练场景"""

from app.models.scenario import ScenarioTemplate
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


async def render_template_opening(template: ScenarioTemplate) -> dict:
    """根据已选场景模板生成开场白与 AI 情绪。

    返回 { initial_message, ai_emotion }
    用 generation_prompt + role_brief + tension_brief 让 LLM 写一句符合人设的开场。
    """
    llm = get_async_llm()
    sys_p = (
        "你是一名场景台词生成器。任务：根据角色画像、张力来源、生成提示，"
        "写出 AI 角色对用户说的第一句话（开场白），并标注 AI 当下的情绪。\n"
        "要求：\n"
        "1. 用真实口语，不要书面化\n"
        "2. 一句到两句之内，体现角色的语气和处境\n"
        "3. 不解释场景、不写旁白、不写括号说明\n"
        "4. 输出 JSON：{\"initial_message\": \"…\", \"ai_emotion\": \"neutral|annoyed|sad|warm|cold|anxious|smug\"}"
    )
    usr_p = (
        f"【角色】{template.role_brief}\n"
        f"【张力】{template.tension_brief}\n"
        f"【生成要求】{template.generation_prompt}\n"
        f"【难度】{template.difficulty}/5\n\n"
        f"请直接输出 JSON。"
    )
    try:
        result = await llm.chat_json(sys_p, usr_p, temperature=0.9)
    except Exception:
        result = {}
    return {
        "initial_message": result.get("initial_message") or template.role_brief,
        "ai_emotion": result.get("ai_emotion", "neutral"),
    }
