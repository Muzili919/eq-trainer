"""P5 真实场景诊断 - 用户提交日记后分析

详见 docs/PROMPTS.md P5 章节"""

SYSTEM = """你是高情商教练。学生记录了一个真实对话场景，你要帮 ta 从中学习。

原则：
1. 不评判对错，描述事实
2. 用苏格拉底反问引导学生自己发现问题
3. 改写示范先藏着，等学生主动要才给
4. 直接输出 JSON"""

USER_TEMPLATE = """## 学生记录的场景
- 背景：{context}
- 对方是：{other_party}
- 对方说："{their_words}"
- 学生说："{my_response}"
- 结果：{outcome}

## 可用技能列表（从中选择识别到的技能）
{skills_json}

## 你的任务
1. 识别这次对话中 1-3 个学生没用好的技能
2. 出 3 个苏格拉底反问（引导，不评判）
3. 准备改写示范（先不展示）

输出 JSON：
{{
  "identified_skills": ["L1", "H1"],
  "diagnosis_brief": "一句话描述（不评判，描述事实）",
  "socratic_questions": [
    "问题1",
    "问题2",
    "问题3"
  ],
  "rewrite_suggestion_hidden": "改写示范，等用户主动要才展示",
  "referenced_style": "huangbo|xuzhisheng|lixueqin|hejiong|none"
}}"""


def build(
    context: str,
    other_party: str,
    their_words: str,
    my_response: str,
    outcome: str,
    skills_json: str,
) -> tuple[str, str]:
    """返回 (system_prompt, user_prompt)"""
    user = USER_TEMPLATE.format(
        context=context,
        other_party=other_party,
        their_words=their_words,
        my_response=my_response,
        outcome=outcome,
        skills_json=skills_json,
    )
    return SYSTEM, user
