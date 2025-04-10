import uuid
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from loguru import logger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.attributes import flag_modified
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from langflow.services.database.models.user.model import User, UserUpdate


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    return (await db.exec(stmt)).first()


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    if isinstance(user_id, str):
        user_id = UUID(user_id)
    stmt = select(User).where(User.id == user_id)
    return (await db.exec(stmt)).first()


async def update_user(user_db: User | None, user: UserUpdate, db: AsyncSession) -> User:
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user.model_dump(exclude_unset=True)
    changed = False
    for attr, value in user_data.items():
        if hasattr(user_db, attr) and value is not None:
            setattr(user_db, attr, value)
            changed = True

    if not changed:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail="Nothing to update")

    user_db.updated_at = datetime.now(timezone.utc)
    flag_modified(user_db, "updated_at")

    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e

    return user_db


async def update_user_last_login_at(user_id: UUID, db: AsyncSession):
    try:
        user_data = UserUpdate(last_login_at=datetime.now(timezone.utc))
        user = await get_user_by_id(db, user_id)
        return await update_user(user, user_data, db)
    except Exception as e:  # noqa: BLE001
        logger.error(f"Error updating user last login at: {e!s}")


async def create_user(
    db: AsyncSession,
    username: str,
    password: str,
    *,
    email: str | None = None,
    is_active: bool = True,
    is_superuser: bool = False,
) -> User:
    from langflow.services.auth.utils import get_password_hash

    hashed_password = get_password_hash(password)
    user = User(
        username=username,
        password=hashed_password,
        email=email,
        is_active=is_active,
        is_superuser=is_superuser,
    )

    db.add(user)
    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail="User already exists.") from e
    return user


async def get_user_by_address_or_create(address: str, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.username == address))
    # print(f"Result: {result}")
    user = result.scalar_one_or_none()

    if user:
        return user

    # Create a new user with the address as username
    return await create_user(
        db=db,
        username=address,
        password=uuid.uuid4().hex,
        email=f"{address}@wallet.local",
        is_active=True,
        is_superuser=False,
    )
