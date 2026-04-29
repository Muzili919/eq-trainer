"""P5 真实场景诊断 - 用户提交日记后分析

详见 docs/PROMPTS.md P5 章节"""

SYSTEM = """你是高情商教练。学生记录了一个真实对话场景，你要帮 ta 从中学习。

原则：
1. 不评判对错，描述事实
2. 用苏格拉底反问引导学生自己发现问题
3. 改写示范先藏着，等学生主动要才给
4. 直接输出 JSON"""

REACT_TEMPLATE = """## 学生记录的场景（被动应对）
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

INITIATE_TEMPLATE = """## 学生准备的场景（主动开口）
- 背景：{context}
- 对方是：{other_party}
- 学生打算这么开口："{my_response}"
- 期望结果：{outcome}

## 可用技能列表（从中选择识别到的技能）
{skills_json}

## 评估视角
学生还**没说**——这是事前预演。你要评估：
1. **开口的得体度**：这个开场会不会让对方一开始就紧绷/反感
2. **铺垫是否够**：直奔主题还是给了对方铺垫
3. **诉求是否清晰**：对方听完知不知道学生想要什么
4. **共情/边界**：是否照顾到对方的处境，但也守住自己的底线

## 你的任务
1. 识别这次开口里 1-3 个**还可以更好的**技能（学生没用足或缺失的）
2. 出 3 个苏格拉底反问（事前预演——帮学生想得更周全）
3. 准备改写示范（先不展示）

输出 JSON：
{{
  "identified_skills": ["L1", "B1"],
  "diagnosis_brief": "一句话描述（不评判，描述这个开场的关键点）",
  "socratic_questions": [
    "对方此刻可能在想什么？",
    "如果你是对方，听到这句话第一反应是什么？",
    "你最希望对方听完做什么？"
  ],
  "rewrite_suggestion_hidden": "更好的开口示范，等用户主动要才展示",
  "referenced_style": "huangbo|xuzhisheng|lixueqin|hejiong|none"
}}"""


def build(
    context: str,
    other_party: str,
    their_words: str,
    my_response: str,
    outcome: str,
    skills_json: str,
    mode: str = "react",
) -> tuple[str, str]:
    """返回 (system_prompt, user_prompt)

    mode="react"（默认）：对方说→我回，评应对
    mode="initiate"：我打算开口，评开场
    """
    if mode == "initiate":
        user = INITIATE_TEMPLATE.format(
            context=context,
            other_party=other_party or "对方",
            my_response=my_response,
            outcome=outcome or "（学生还没说，正在准备）",
            skills_json=skills_json,
        )
    else:
        user = REACT_TEMPLATE.format(
            context=context,
            other_party=other_party or "对方",
            their_words=their_words or "（未填）",
            my_response=my_response,
            outcome=outcome or "（未填）",
            skills_json=skills_json,
        )
    return SYSTEM, user
