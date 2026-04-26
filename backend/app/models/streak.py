from datetime import date

from sqlmodel import Field, SQLModel, UniqueConstraint


class DailyStreak(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True, index=True)

    current_streak: int = 0
    longest_streak: int = 0
    last_active_date: date | None = None
    total_days: int = 0


class DailyLog(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("user_id", "log_date", name="uq_user_date"),)

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    log_date: date = Field(index=True)

    practices_completed: int = 0
    avg_score: float | None = None
    diary_count: int = 0
