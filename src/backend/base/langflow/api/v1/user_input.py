from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

# Assuming these dependencies exist in Langflow

from langflow.api.utils import DbSession
from langflow.services.database.models.user.model import User
from langflow.services.database.models.user_input import UserInput
from langflow.services.database.models.user_input.crud import (
    get_user_input_by_id,
    create_user_input,
    update_user_input,
    delete_user_input
)

router = APIRouter(tags=["user_input"],prefix="/user_input")

@router.get("/", response_model=UserInput)
async def read_user_input(
    db: DbSession,
    id: str = Query(..., description="The UUID of the user input to retrieve")
)-> UserInput:
    """
    Retrieve a UserInput by ID. Authorization: only the target user can access.
    """
    ui = await get_user_input_by_id(db, id)
    if not ui:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Input not found")
    return ui

@router.post("/", response_model=UserInput, status_code=status.HTTP_201_CREATED)
async def create_user_input_endpoint(
    data: dict,
    target_user_id: str,
    db: DbSession,
    current_user: User,
):
    """
    Create a new UserInput. Authorization: user can only create for themselves.
    """
    if target_user_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    ui = await create_user_input(db, data, target_user_id)
    return ui

@router.put("/", response_model=UserInput)
async def update_user_input_endpoint(
    db: DbSession,
    current_user: User,
    id: str = Query(..., max_length=32),
    data: dict = None,
):
    """
    Update an existing UserInput. Authorization: only the target user can update.
    """
    ui = await get_user_input_by_id(db, id)
    if not ui:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Input not found")
    if ui.target_user_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    updated = await update_user_input(db, ui, data)
    return updated

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_input_endpoint(
    db: DbSession,
    current_user: User,
    id: str = Query(..., max_length=32),     
):
    """
    Delete a UserInput. Authorization: only the target user can delete.
    """
    ui = await get_user_input_by_id(db, id)
    if not ui:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Input not found")
    if ui.target_user_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    await delete_user_input(db, ui)