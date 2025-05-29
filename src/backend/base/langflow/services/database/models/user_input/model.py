from uuid import uuid4
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field
from typing import Any, Optional
from sqlalchemy import JSON

class UserInput(SQLModel, table=True):
    __tablename__ = "user_input"

    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True, max_length=32)
    data: Optional[dict] = Field(
        default=None,
        sa_type=JSON
    )
    target_user_id: str = Field(foreign_key="user.id", max_length=36, nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)