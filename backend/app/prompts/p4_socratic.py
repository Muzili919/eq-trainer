"""P4 苏格拉底引导 - 评分 < 70 时触发，最多 3 次

详见 docs/PROMPTS.md P4 章节"""

SYSTEM = """你是苏格拉底式高情商教练。学生的回应还不够好，你的任务是用 1 个问题让 ta 自己想到正确方向。

原则：
1. 不直接告诉错在哪——只问问题
2. 触发反思，不触发挫败
3. 1 个问题，简短口语化，后面带温和鼓励
4. 直接输出 JSON"""

USER_TEMPLATE = """学生在【{skill_name}】练习中给出了不到位的回应。

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

输出 JSON：
{{
  "question": "你的引导问题",
  "encouragement": "鼓励性短句（一句话）"
}}"""


def build(
    skill_name: str,
    context: str,
    user_response: str,
    ai_feedback: str,
    used_questions: str,
) -> tuple[str, str]:
    """返回 (system_prompt, user_prompt)"""
    user = USER_TEMPLATE.format(
        skill_name=skill_name,
        context=context,
        user_response=user_response,
        ai_feedback=ai_feedback,
        used_questions=used_questions,
    )
    return SYSTEM, user
