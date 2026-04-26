"""P3 评分判断引擎 - 4 维度灵活评分 + 风格匹配 + 描述性反馈

详见 docs/PROMPTS.md P3 章节"""

SYSTEM = """你是高情商沟通教练。你的任务是评估用户在对话场景中的回应质量，并给出风格化的反馈。

评分原则：
1. 不打"对/错"，只描述"好在哪、怎么更好"
2. 4 个维度独立打分（0-100），不互相替代
3. 必须输出严格的 JSON，不要任何解释文字
4. 风格匹配：从 黄渤/徐志胜/李雪琴/何炅 4 人里选一个最像的，没明显风格则 "none"
"""

USER_TEMPLATE = """## 场景
{scenario_setup}

## 对话历史
{dialog_history}

## 用户最新回应（评估对象）
"{user_response}"

## 主练技能
{target_skill}

## 风格基准参考（few-shot 学习）
{style_references}

## 评分维度（每项 0-100）

**1. 得体度（decency）**
- 100 = 不冒犯、不油腻、合场合
- 60 = 中规中矩
- 30 = 有冒犯/油腻倾向

**2. 化解力（defusion）**
- 100 = 把潜在冲突/尴尬卸了
- 60 = 没让局面变差，但也没真化解
- 30 = 让局面更尴尬/对方更不满

**3. 幽默指数（humor）**
- 100 = 有梗、有错位、有自嘲，能让对方笑或想笑
- 60 = 有调皮但不出彩
- 30 = 完全严肃或干涩

**4. 风格匹配度（style_match）**
判断这条回应最像 4 人中哪位的风格。
- 100 = 极度像（用词、思路、节奏都到位）
- 60 = 有那个味道但不够
- 30 = 跟 4 位都不像（也可以选 "none"）

## 反馈要求

不要说"对/错"。给：
1. 这条回应**好的地方**（具体到字、词、手法）
2. **可以更好的方向**（不止一种）
3. **改写示范**（如果总分 < 70，给 1 个高分版本，标注是哪种风格）

## 输出严格 JSON

{{
  "scores": {{
    "decency": 0-100,
    "defusion": 0-100,
    "humor": 0-100,
    "style_match": 0-100
  }},
  "style_matched": "huangbo|xuzhisheng|lixueqin|hejiong|none",
  "strengths": "好在哪（一两句话）",
  "improvements": "可以更好的方向",
  "rewrite_suggestion": "改写示范（可选，总分<70 时给）",
  "referenced_style_excerpt": "如果改写借鉴了 4 位中谁的某句风格，标出来；否则 null"
}}
"""


def build(
    scenario_setup: str,
    dialog_history: str,
    user_response: str,
    target_skill: str,
    style_references: str,
) -> tuple[str, str]:
    """返回 (system_prompt, user_prompt)"""
    user = USER_TEMPLATE.format(
        scenario_setup=scenario_setup,
        dialog_history=dialog_history,
        user_response=user_response,
        target_skill=target_skill,
        style_references=style_references,
    )
    return SYSTEM, user
