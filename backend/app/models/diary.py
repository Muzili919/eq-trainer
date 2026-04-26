from datetime import datetime

from sqlmodel import Field, SQLModel


class Diary(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)

    context: str
    other_party: str | None = None
    their_words: str
    my_response: str
    outcome: str | None = None

    created_at: datetime = Field(default_factory=datetime.utcnow)


class DiaryAnalysis(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    diary_id: int = Field(foreign_key="diary.id", unique=True, index=True)

    identified_skills: str       # JSON 数组 ["L1", "H1"]
    diagnosis_brief: str | None = None
    socratic_questions: str      # JSON 数组
    rewrite_suggestion_hidden: str | None = None  # 默认隐藏，用户求才展示
    referenced_style: str | None = None           # huangbo|xuzhisheng|...

    created_at: datetime = Field(default_factory=datetime.utcnow)
