# app/routes/adminRoutes.py
from fastapi import APIRouter, Depends
from app.utils.admin_verification import verify_admin
from app.services.adminService import (
    delete_all_users_admin_service,
    get_all_users_admin_service,
    get_user_by_id_admin_service,
    delete_user_admin_service,
)

router = APIRouter(
    tags=["Admin"],
    dependencies=[Depends(verify_admin)]  # Enforce admin access for all routes
)


@router.delete("/users")
async def delete_all_users():
    """
    Delete all users. Admin access required.
    """
    result = delete_all_users_admin_service()
    return result


@router.get("/users")
async def get_all_users():
    """
    Retrieve all users. Admin access required.
    """
    users = get_all_users_admin_service()
    return users


@router.get("/{user_id}")
async def get_user_by_id(user_id: str):
    """
    Retrieve a user by their ID. Admin access required.
    """
    user = get_user_by_id_admin_service(user_id)
    return user


@router.delete("/{user_id}")
async def delete_user(user_id: str):
    """
    Delete a user by their ID. Admin access required.
    """
    return delete_user_admin_service(user_id)
