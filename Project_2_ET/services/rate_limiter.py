from fastapi import HTTPException ,Depends
from datetime import timedelta
import redis.asyncio as redis
from .auth import get_current_user


client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

ROLE_LIMITS={
    "ADMIN":90,
    "USER":20,
    "GUEST":7
}

async def Rate_limiter(curr_user=Depends(get_current_user)):

    limit = ROLE_LIMITS.get(curr_user.role,5)

    key = f"rate_limiter:{curr_user.role}:{curr_user.user_id}"

    count = await client.incr(key)

    if count==1 :

        await client.expire(key,timedelta(minutes=1))

    if count > limit :
        raise HTTPException(
            status_code=429,
            detail=f"Rate Limit Exceeded! --- Allowed Limits : {limit}/min"
        )
    