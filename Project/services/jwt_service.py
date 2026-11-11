from datetime import datetime,timedelta,timezone
from jose import jwt,JWTError   
from typing import Any 


class JWTService:

    SECRET = "python-fastapi-aqswde"
    ALOGORITHM = "HS256"
    EXPIRY_TIME_IN_MINUTES = 5
    EXPIRY_TIME_IN_DAYS = 7

    def Create_Assess_Token(self,email:str) -> str:

        data = {"email":email}

        expire = datetime.now(timezone.utc) + timedelta(minutes=JWTService.EXPIRY_TIME_IN_MINUTES) # get the expire time form the currect time

        data.update({
            "exp":expire
            })

        return jwt.encode(data,
            JWTService.SECRET,
            algorithm=JWTService.ALOGORITHM
        )
  
    def Create_Refresh_Token(self,email:str) -> str:

        data = {"email":email}

        expire = datetime.now(timezone.utc) + timedelta(days=JWTService.EXPIRY_TIME_IN_DAYS) # get the expire time form the currect time

        data.update({
            "exp":expire
            })

        return jwt.encode(data,
            JWTService.SECRET,
            JWTService.ALOGORITHM
        )

    def decode(self,token:str) -> dict[str|any]|None :
        try:
            return jwt.decode(
                token,
                JWTService.SECRET,
                algorithms=[JWTService.ALOGORITHM]
            )
        except JWTError as ex:
            print(f"Exception in JWT Decode : {str(ex)}")
            return None
