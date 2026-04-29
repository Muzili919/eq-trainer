from datetime import datetime

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, max_length=32)
    password_hash: str
    nickname: str | None = None

    target_style: str = "huangbo"
    target_styles: str = "[]"  # JSON array, e.g. ["huangbo","hejiong","caikangyong"]
    humor_weight: float = 0.30
    target_role: str = "general"  # general | property_manager | decoration_boss | beauty_clinic_boss

    daily_goal: int = 3
    voice_input_enabled: bool = True

    plan: str = "free"  # free | premium
    plan_expires_at: datetime | None = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active_at: datetime | None = None
