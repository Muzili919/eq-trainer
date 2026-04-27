"""角色扮演服务 - 调用 P2，AI 扮演对方推进对话"""

import logging

from app.prompts import p2_roleplay
from app.services.llm import get_async_llm

log = logging.getLogger(__name__)


async def get_ai_reply(
    role_brief: str,
    scenario_setup: str,
    dialog_history: str,
    user_response: str,
    turn_number: int,
) -> dict:
    """
    返回 AI 角色的下一句话：
    { message, emotion, should_end }
    """
    try:
        llm = get_async_llm()
        sys_p, usr_p = p2_roleplay.build(
            role_brief=role_brief,
            scenario_setup=scenario_setup,
            dialog_history=dialog_history,
            user_response=user_response,
            turn_number=turn_number,
        )
        result = await llm.chat_json(sys_p, usr_p, temperature=0.8)
        if result and result.get("message"):
            return {
                "message": result["message"],
                "emotion": result.get("emotion", "neutral"),
                "should_end": result.get("should_end", False),
                "fallback": False,
            }
    except Exception as e:
        log.error("get_ai_reply failed: %s", e)

    # AI 完全失败时返回兜底标志，前端识别后展示"重试"提示而不是当真对方说的话
    return {
        "message": "（连接对方的信号弱了一下，再试一次？）",
        "emotion": "neutral",
        "should_end": False,
        "fallback": True,
    }
