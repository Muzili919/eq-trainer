from datetime import datetime

from sqlmodel import Field, SQLModel


class InvitationCode(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(unique=True, index=True, max_length=32)
    plan_type: str = "premium"
    duration_days: int = 30
    max_uses: int | None = 1
    used_count: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
