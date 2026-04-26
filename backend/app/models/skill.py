from datetime import datetime

from sqlmodel import Field, SQLModel, UniqueConstraint


class Skill(SQLModel, table=True):
    """静态种子数据（从 SKILLS.md 导入），不随用户变化"""

    id: str = Field(primary_key=True, max_length=8)  # 'L1', 'H2'
    category: str = Field(max_length=32)
    name: str = Field(max_length=32)
    name_en: str = Field(max_length=64)
    stage: str = Field(max_length=16)  # basic | mid | advanced

    description: str
    patterns: str  # JSON array
    examples_good: str  # JSON array
    examples_bad: str  # JSON array
    socratic_prompts: str  # JSON array
    prerequisites: str = "[]"  # JSON array

    icon: str | None = None
    color: str | None = None
    sort_order: int = 0


class SkillProgress(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("user_id", "skill_id", name="uq_user_skill"),)

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    skill_id: str = Field(foreign_key="skill.id", index=True, max_length=8)

    level: int = 0  # 0-5
    correct_streak: int = 0
    total_attempts: int = 0
    avg_score: float = 0.0

    last_practiced_at: datetime | None = None
    next_review_at: datetime | None = Field(default=None, index=True)
