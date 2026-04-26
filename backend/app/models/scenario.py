from sqlmodel import Field, SQLModel


class ScenarioTemplate(SQLModel, table=True):
    """场景模板（种子数据）。AI 据此实时生成具体台词，不写死回答"""

    id: int | None = Field(default=None, primary_key=True)

    category: str = Field(max_length=32)  # workplace | social | family | romance | self
    sub_type: str = Field(max_length=64)
    title: str

    role_brief: str  # AI 扮演的角色画像
    tension_brief: str  # 冲突/张力来源
    user_goal_brief: str  # 用户在这场对话里的合理目标

    primary_skills: str  # JSON 数组：本场景主要练哪些技能 id
    difficulty: int = 3  # 1-5

    applicable_roles: str = '["general"]'  # JSON 数组，可包含 general/property_manager/decoration_boss

    generation_prompt: str  # AI 生成具体台词的 prompt 模板（含变量占位）
