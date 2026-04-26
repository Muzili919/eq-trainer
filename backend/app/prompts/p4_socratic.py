"""P4 苏格拉底引导 - 评分 < 60 时触发，最多 3 次

详见 docs/PROMPTS.md P4 章节"""

SYSTEM = """你是苏格拉底式高情商教练。学生的回应还不够好，你的任务是用 1 个问题让 ta 自己想到正确方向。

原则：
1. 不直接告诉错在哪——只问问题
2. 触发反思，不触发挫败——尤其低分时更要温和，不要追问太猛
3. 1 个问题，简短口语化，后面带温和鼓励
4. 根据学生分数调整语气：30 分以下是"没关系，我们慢慢来"，50 分以上是"差一点点就能更好"
5. 直接输出 JSON"""

USER_TEMPLATE = """学生在【{skill_name}】练习中给出了不到位的回应（得分 {total_score}/100）。

## 场景与对话
{context}

## 学生的回应
"{user_response}"

## AI 评分反馈
{ai_feedback}

## 本场已经问过的引导问题（不要重复）
{used_questions}

问 1 个问题，满足：
- 引向【{skill_name}】这个技能的核心
- 跟之前问过的不重复
- 1-2 句话，口语化
- {score_guidance}

输出 JSON：
{{
  "question": "你的引导问题",
  "encouragement": "鼓励性短句（一句话）"
}}"""


def _score_guidance(score: float) -> str:
    if score < 30:
        return "语气要特别温和，不要施压，让学生感受到安全感"
    if score < 45:
        return "语气温和但有方向感，帮学生看到一线希望"
    return "差一点就到位了，帮学生自己想到那个关键点"


def build(
    skill_name: str,
    context: str,
    user_response: str,
    ai_feedback: str,
    used_questions: str,
    total_score: float = 50,
) -> tuple[str, str]:
    """返回 (system_prompt, user_prompt)"""
    user = USER_TEMPLATE.format(
        skill_name=skill_name,
        context=context,
        user_response=user_response,
        ai_feedback=ai_feedback,
        used_questions=used_questions,
        total_score=round(total_score),
        score_guidance=_score_guidance(total_score),
    )
    return SYSTEM, user
