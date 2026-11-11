from fastapi import Depends, HTTPException,Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from services import JWTService
from config.db import get_db
from Models.user_model import UserModel

security = HTTPBearer()


async def get_current_user(
    request:Request,
    bearer_token: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> UserModel:

   
    token = bearer_token.credentials

    

    payload = JWTService().decode(token=token)

  

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid Token !!!"
        )

    email = payload.get("email")

    result = await db.execute(
        select(UserModel).where(
            UserModel.email == email
        )
    )

    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User Not Found !!!"
        )
    
    request.state.current_user=user

    return user

    