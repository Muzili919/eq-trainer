"""评分服务 - 调用 P3 + P6，计算加权总分"""

import asyncio
import logging

from app.prompts import p3_scoring, p6_skill_identify
from app.services.llm import get_async_llm

log = logging.getLogger(__name__)


def _compute_total(scores: dict, humor_weight: float) -> float:
    """4 维度加权汇总，归一化确保 sum(weights) = 1"""
    base = {"decency": 0.25, "defusion": 0.30, "style_match": 0.15}
    scale = (1 - humor_weight) / sum(base.values())
    weights = {k: v * scale for k, v in base.items()}
    weights["humor"] = humor_weight
    return sum(scores.get(k, 0) * weights[k] for k in weights)


async def score_response(
    scenario_setup: str,
    dialog_history: str,
    user_response: str,
    target_skill: str,
    style_references: str,
    their_words: str,
    skills_compact_list: str,
    humor_weight: float = 0.30,
    target_styles: list[str] | None = None,
    turn_number: int = 1,
) -> dict:
    try:
        llm = get_async_llm()
        p3_sys, p3_usr = p3_scoring.build(
            scenario_setup=scenario_setup,
            dialog_history=dialog_history,
            user_response=user_response,
            target_skill=target_skill,
            style_references=style_references,
            target_styles=target_styles,
            turn_number=turn_number,
        )
        p6_sys, p6_usr = p6_skill_identify.build(
            their_words=their_words,
            user_response=user_response,
            skills_compact_list=skills_compact_list,
        )

        p3_result, p6_result = await asyncio.gather(
            llm.chat_json(p3_sys, p3_usr, temperature=0.4),
            llm.chat_json(p6_sys, p6_usr, temperature=0.2),
        )

        if not p3_result:
            p3_result = {}
        scores = p3_result.get("scores", {})
        total = _compute_total(scores, humor_weight)

        # 处理 rewrite_suggestions：可能是 list 或旧格式 str
        raw_rewrites = p3_result.get("rewrite_suggestions")
        rewrite_suggestions = []
        if isinstance(raw_rewrites, list):
            rewrite_suggestions = raw_rewrites
        elif raw_rewrites:
            # 旧格式兼容
            rewrite_suggestions = [{"style": "unknown", "text": str(raw_rewrites)}]

        return {
            **p3_result,
            "total_score": round(total, 1),
            "well_used": p6_result.get("well_used", []) if p6_result else [],
            "missing": p6_result.get("missing", []) if p6_result else [],
            "rewrite_suggestions": rewrite_suggestions,
        }
    except Exception as e:
        log.error("score_response failed: %s", e)
        return {
            "scores": {"decency": 0, "defusion": 0, "humor": 0, "style_match": 0},
            "total_score": 0,
            "strengths": "",
            "improvements": "评分暂时出了点问题，这轮不计分。",
            "rewrite_suggestion": None,
            "rewrite_suggestions": [],
            "narrative": "评分暂时出了点问题，这轮会自动跳过。",
            "techniques_used": [],
            "techniques_available": [],
            "well_used": [],
            "missing": [],
        }
