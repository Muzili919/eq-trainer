"""P3 评分判断引擎 - 4 维度评分 + 手法识别 + 多风格改写

详见 docs/PROMPTS.md P3 章节"""

SYSTEM = """你是高情商沟通教练。你的任务是评估用户在对话场景中的回应质量，识别使用的手法，并给出多风格改写示范。

评分原则：
1. 不打"对/错"，只描述"好在哪、怎么更好"
2. 4 个维度独立打分（0-100），不互相替代
3. 从手法库中识别用户使用了哪些手法
4. 建议还可以使用的手法
5. 必须输出严格的 JSON，不要任何解释文字
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

## 手法库
{technique_library}

## 用户正在学习的风格路线
{user_style_routes}

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
判断这条回应最像用户正在学习的哪个风格路线。

## 反馈要求

不要说"对/错"。给：
1. 这条回应**好的地方**（具体到字、词、手法）
2. **可以更好的方向**（不止一种）
3. **手法识别**：从上面的手法库中选出用户实际使用的手法（1-3个）
4. **手法建议**：从用户正在学习的风格路线对应的手法中，建议还可以用哪些（1-3个）
5. **风格参考答案**：每个风格路线对应的人物，如果**处在用户的位置**（面对 AI 扮演的对方），会用他自己的风格怎么回应。注意：人物是帮**用户**出主意，不是帮 AI 对方说话！人物和用户站在同一侧，面对的是场景中的对方。

⚠️ 立场校验：写风格参考答案前，先确认——这个回答是用户对对方说的，还是对方对用户说的？必须是**用户对对方说**。如果写成了对方的立场，那就是错的。

## 输出严格 JSON

{{
  "scores": {{
    "decency": 0-100,
    "defusion": 0-100,
    "humor": 0-100,
    "style_match": 0-100
  }},
  "style_matched": "最像的风格ID",
  "techniques_used": ["识别到的手法1", "手法2"],
  "techniques_available": ["建议使用的手法1", "手法2"],
  "narrative": "用教练口吻写的 2-3 句话总结。站在用户这边，说：你（用户）面对对方时做了什么→效果如何→下一步可以怎样。注意：你是在教用户怎么回应对方，不是在替对方说话。",
  "strengths": "好在哪（一两句话）",
  "improvements": "可以更好的方向",
  "rewrite_suggestions": {rewrite_format}
}}
"""


def build(
    scenario_setup: str,
    dialog_history: str,
    user_response: str,
    target_skill: str,
    style_references: str,
    target_styles: list[str] | None = None,
) -> tuple[str, str]:
    """返回 (system_prompt, user_prompt)"""
    from app.data.styles import (
        TECHNIQUES, STYLES,
        build_technique_prompt_block,
        build_style_rewrite_block,
    )

    if not target_styles:
        target_styles = ["huangbo", "hejiong", "caikangyong"]

    # 构建手法库文本
    tech_lines = []
    for name, desc in TECHNIQUES.items():
        tech_lines.append(f"- {name}：{desc}")
    technique_library = "\n".join(tech_lines)

    # 构建用户风格路线文本
    style_route_parts = []
    for sid in target_styles:
        s = STYLES.get(sid)
        if s:
            style_route_parts.append(f"- {s['name']}（{s['school']}）：{'、'.join(s['learn'])}")
    user_style_routes = "\n".join(style_route_parts)

    # 构建改写格式
    rewrite_format = build_style_rewrite_block(target_styles)

    user = USER_TEMPLATE.format(
        scenario_setup=scenario_setup,
        dialog_history=dialog_history,
        user_response=user_response,
        target_skill=target_skill,
        style_references=style_references,
        technique_library=technique_library,
        user_style_routes=user_style_routes,
        rewrite_format=rewrite_format,
    )
    return SYSTEM, user
