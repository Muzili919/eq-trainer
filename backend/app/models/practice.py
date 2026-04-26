from datetime import datetime

from sqlmodel import Field, SQLModel


class Practice(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    skill_id: str = Field(foreign_key="skill.id", max_length=8)

    scenario_title: str | None = None
    scenario_setup: str | None = None
    role_brief: str | None = None
    difficulty: int = 3

    avg_score: float | None = None
    completed_at: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PracticeTurn(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    practice_id: int = Field(foreign_key="practice.id", index=True)
    turn_number: int
    turn_type: str = Field(default="dialogue", max_length=16)  # dialogue | reflection

    user_input: str = Field(default="")
    user_input_mode: str = Field(default="text", max_length=8)  # text | voice

    ai_message: str | None = None
    ai_emotion: str | None = None
    coach_followup: str | None = None  # reflection 模式下教练的回复

    score_decency: float | None = None
    score_defusion: float | None = None
    score_humor: float | None = None
    score_style_match: float | None = None
    total_score: float | None = None

    strengths: str | None = None
    improvements: str | None = None
    rewrite_suggestion: str | None = None

    socratic_question: str | None = None
    socratic_attempts: int = 0

    well_used_skills: str | None = None   # JSON 数组
    missing_skills: str | None = None     # JSON 数组

    created_at: datetime = Field(default_factory=datetime.utcnow)
