from sqlmodel import Field, SQLModel


class StyleReference(SQLModel, table=True):
    """风格基准条目 - prompt few-shot 弹药库（静态种子数据）"""

    id: int | None = Field(default=None, primary_key=True)

    persona: str = Field(max_length=16, index=True)  # huangbo | xuzhisheng | lixueqin | hejiong
    scenario_type: str = Field(max_length=32, index=True)
    # praised | attacked | awkward | rejected | comforting | tease | pressured | compared | other

    trigger: str  # 对方说了啥
    response: str  # ta 怎么回
    technique: str  # JSON 数组：用到的技能 id

    notes: str | None = None
    source: str | None = None
