"""P6 技能识别 - 轻量分类器，每次评分时附带调用

详见 docs/PROMPTS.md P6 章节"""

SYSTEM = """分析对话回应中体现的高情商技能。直接输出 JSON，不要解释。"""

USER_TEMPLATE = """对方说："{their_words}"
用户说："{user_response}"

## 技能列表
{skills_compact_list}

识别最相关的 1-3 个技能 id，区分"用得好"和"应该用但没用到"。

输出 JSON：
{{
  "well_used": ["L1"],
  "missing": ["H1", "EM2"]
}}"""


def build(
    their_words: str,
    user_response: str,
    skills_compact_list: str,
) -> tuple[str, str]:
    """返回 (system_prompt, user_prompt)"""
    user = USER_TEMPLATE.format(
        their_words=their_words,
        user_response=user_response,
        skills_compact_list=skills_compact_list,
    )
    return SYSTEM, user
