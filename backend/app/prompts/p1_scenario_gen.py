"""P1 场景生成器 - 根据技能/难度/用户偏好生成训练场景

详见 docs/PROMPTS.md P1 章节"""

SYSTEM = """你是 EQ Trainer 的场景出题专家。任务是为用户生成真实感强、有压力感的对话练习场景。

原则：
1. 场景日常真实，不要刻意（避免"领导找你谈话"这种烂俗设定）
2. 对方开口要能"cue 住"用户——让人想回但不知怎么回
3. 不给提示，不在 setup 里暗示标准答案
4. scenario_setup 里写场景背景时，**用户是面对这个场景的人**；AI 扮演的对方是给用户制造压力的角色
5. 角色、立场必须自洽——如果 scenario 说"你被朋友放鸽子"，那 AI 就扮演放鸽子的那个朋友，而不是反过来
6. 直接输出 JSON，不要任何解释"""

USER_TEMPLATE = """生成一道 {difficulty}/5 难度的对话练习场景，重点训练【{skill_name}】。

## 关于该技能
{skill_description}
关键模式：{skill_patterns}

## 用户画像
- 历史风格偏好：{user_style_preference}
- 近期平均分：{recent_avg_score}
- 已练过的场景类型（避免重复）：{used_categories}

## 风格倾向
目标风格：{user_target_style}
如果目标含 humor 元素，场景里加能玩梗的钩子；如果是严肃风，场景更正式。

## 难度说明
- 1分：对方友善、压力小，适合新手
- 3分：有轻度冲突/尴尬，需要化解
- 5分：对方有攻击性/冒犯性，高压场景

## 输出 JSON
{{
  "title": "一句话场景标题",
  "scenario_setup": "2-3 句话描述场景背景（给用户读的）",
  "role_brief": "你（AI）扮演的角色画像：身份/关系/此刻心情/你在这个场景中做了什么（必须与 scenario_setup 的立场一致）",
  "initial_message": "对方开口的第一句话（这是对话起点）",
  "ai_emotion": "neutral|annoyed|sarcastic|playful|sad|expectant",
  "category": "work|friend|family|stranger|date|online"
}}

直接输出 JSON，不要解释。"""


def build(
    skill_name: str,
    skill_description: str,
    skill_patterns: str,
    difficulty: int,
    user_style_preference: str,
    user_target_style: str,
    recent_avg_score: float,
    used_categories: str,
) -> tuple[str, str]:
    """返回 (system_prompt, user_prompt)"""
    user = USER_TEMPLATE.format(
        skill_name=skill_name,
        skill_description=skill_description,
        skill_patterns=skill_patterns,
        difficulty=difficulty,
        user_style_preference=user_style_preference,
        user_target_style=user_target_style,
        recent_avg_score=recent_avg_score,
        used_categories=used_categories,
    )
    return SYSTEM, user
