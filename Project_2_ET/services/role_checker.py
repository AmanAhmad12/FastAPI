from fastapi import Depends, HTTPException, status

from .auth import get_current_user
from Models.user_model import UserModel


def require_roles(*allowed_roles):

    async def checker(
        current_user: UserModel = Depends(get_current_user)
    ):

        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access Denied"
            )

        return current_user

    return checker