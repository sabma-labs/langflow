import logging
from uuid import uuid4
from typing import Any, Optional
from datetime import datetime, timezone
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from langflow.services.database.models.user_input import UserInput


logger = logging.getLogger(__name__)

async def get_user_input_by_id(db: AsyncSession, input_id: str) -> Optional[UserInput]:
    """
    Retrieve a UserInput by its ID.
    Returns None if not found or on error.
    """
    try:
        stmt = select(UserInput).where(UserInput.id == input_id)
        result = await db.exec(stmt)
        return result.first()
    except Exception as e:
        logger.exception(f"Error fetching UserInput with id %s: %s", input_id, e)
        return None

async def create_user_input(db: AsyncSession, data: Any, target_user_id: str) -> Optional[UserInput]:
    """
    Create a new UserInput record.
    Returns the new UserInput or None on failure.
    """
    ui = UserInput(id=str(uuid4()), data=data, target_user_id=target_user_id)
    try:
        async with db.begin():
            db.add(ui)
        # after commit, refresh to populate defaults
        await db.refresh(ui)
        return ui
    except Exception as e:
        await db.rollback()
        logger.exception("Failed to create UserInput: %s", e)
        return None

async def update_user_input(
    db: AsyncSession, existing: UserInput, data: Any
) -> Optional[UserInput]:
    """
    Update the data payload of an existing UserInput.
    Returns the updated UserInput or None on failure.
    """
    try:
        existing.data = data
        existing.updated_at = datetime.now(timezone.utc)
        async with db.begin():
            db.add(existing)
        await db.refresh(existing)
        return existing
    except Exception as e:
        await db.rollback()
        logger.exception("Failed to update UserInput with id %s: %s", existing.id, e)
        return None

async def delete_user_input(db: AsyncSession, existing: UserInput) -> bool:
    """
    Delete an existing UserInput.
    Returns True on success, False on failure.
    """
    try:
        async with db.begin():
            await db.delete(existing)
        return True
    except Exception as e:
        await db.rollback()
        logger.exception("Failed to delete UserInput with id %s: %s", existing.id, e)
        return False
