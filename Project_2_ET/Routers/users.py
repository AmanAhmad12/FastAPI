from datetime import datetime
from uuid import UUID, uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field
)

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from passlib.context import CryptContext

from config.db import get_db
from Models import UserModel
from services import HashService, JWTService

from services import require_roles


# ============================================================
# Router
# ============================================================

users = APIRouter(
    prefix="/user",
    tags=["Users Routes"]
)

# ============================================================
# Password Encryption Configuration
# ============================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# ============================================================
# Base Response
# ============================================================

class BaseOut(BaseModel):
    msg: str
    error: str | None = None


# ============================================================
# User Pydantic Model
# ============================================================

class Users(BaseModel):
    user_id: UUID = Field(default_factory=uuid4)
    user_name: str
    email: EmailStr
    password: str
    role: str
    refresh_token: str | None = None
    created_at: datetime = Field(
        default_factory=datetime.now
    )

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# User Create Request Model
# ============================================================

class Users_Create(BaseModel):
    user_name: str
    email: EmailStr
    password: str

# ============================================================
# User Response Model
# ============================================================

class UserResponse(BaseModel):
    data: list[Users] = Field(default_factory=list)
    msg: str
    error: str = "*** NO ERROR ***"


# ============================================================
# Login Request Model
# ============================================================

class SignIn(BaseModel):
    email: EmailStr
    password: str


# ============================================================
# Refresh Token Request Model
# ============================================================

class RefreshToken(BaseModel):
    refresh_token: str


# ============================================================
# JWT Output Response
# ============================================================

class JWTOut(BaseOut):
    Assess_token: str
    Refresh_token: str


# ============================================================
# SIGNUP
# ============================================================

@users.post("/signup",response_model=UserResponse)
async def User_SignUp(user: Users_Create,db: AsyncSession = Depends(get_db)):

    # --------------------------------------------------------
    # Check whether email already exists
    # --------------------------------------------------------

    result = await db.execute(
        select(UserModel).where(
            UserModel.email == user.email
        )
    )

    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="User Already Exists !!!"
        )

    # --------------------------------------------------------
    # Encrypt password before storing
    # --------------------------------------------------------

    hashed_password = HashService(
        pwd_context=pwd_context
    ).hash_password(
        user.password
    )


    # --------------------------------------------------------
    # Create SQLAlchemy Object
    # --------------------------------------------------------

    user_model = UserModel(
        user_name=user.user_name,
        email=user.email,
        password=hashed_password,
        role="USER"
    )

    # --------------------------------------------------------
    # Add into database
    # --------------------------------------------------------

    db.add(user_model)

    await db.commit()
    await db.refresh(user_model)

    return UserResponse(
        data=[
            Users.model_validate(user_model)
        ],
        msg="USER SUCCESSFULLY SIGNED UP"
    )


# ============================================================
# SIGNIN
# ============================================================

@users.post("/signin",response_model=JWTOut)
async def User_SignIn(user: SignIn,db: AsyncSession = Depends(get_db)
):

    # --------------------------------------------------------
    # Find user using email
    # --------------------------------------------------------

    # print("Entered Password:", user.password)

    

    result = await db.execute(
        select(UserModel).where(
            UserModel.email == user.email
        )
    )


    user_model = result.scalars().first()


    if not user_model:
        raise HTTPException(
        status_code=401,
        detail="Invalid Email Or Password  OR USER NOT FOUND"
    )

    # --------------------------------------------------------
    # Verify Password
    # --------------------------------------------------------

    # print("Input Email:", user.email)
    # print("Input Password:", repr(user.password))
    # print("DB Hash:", user_model.password)

    is_valid_password = HashService(
        pwd_context=pwd_context
    ).verify_hash_password(
        user.password,
        user_model.password
    )

    print("Password Match:", is_valid_password)

    if not is_valid_password:
        raise HTTPException(
            status_code=401,
            detail="Invalid Email Or Password"
        )

    # --------------------------------------------------------
    # Generate Access Token
    # --------------------------------------------------------

    access_token = JWTService().Create_Assess_Token(
        email=user_model.email,
        role=user_model.role
    )

    # --------------------------------------------------------
    # Generate Refresh Token
    # --------------------------------------------------------

    refresh_token = JWTService().Create_Refresh_Token(
        email=user_model.email,
        role=user_model.role
    )

    # --------------------------------------------------------
    # Save Refresh Token in DB
    # --------------------------------------------------------

    user_model.refresh_token = refresh_token

    await db.commit()
    await db.refresh(user_model)

    return JWTOut(
        Assess_token=access_token,
        Refresh_token=refresh_token,
        msg="User Login Successfully !!!"
    )




# ============================================================
# GET ALL USERS      (ROLE BASED EXCESS !!!!)
# ============================================================

@users.get("/all",response_model=UserResponse)

async def Get_All_Users(db: AsyncSession = Depends(get_db),current_user=Depends(require_roles("ADMIN"))):# here for invalid user the currect_user return the asscess denied 

    result = await db.execute(
        select(UserModel)
    )

    user_models = result.scalars().all()

    return UserResponse(
        data=[
            Users.model_validate(user)
            for user in user_models
        ],
        msg="Users Fetched Successfully"
    )


# ============================================================
# REFRESH TOKEN
# ============================================================

@users.post("/refresh",response_model=JWTOut)
async def Refresh_Token(payload: RefreshToken,db: AsyncSession = Depends(get_db)):

    # --------------------------------------------------------
    # Decode Refresh Token
    # --------------------------------------------------------

    decoded_value = JWTService().decode(
        token=payload.refresh_token
    )

    if decoded_value is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid Refresh Token"
        )

    # --------------------------------------------------------
    # Get Email from Token
    # --------------------------------------------------------

    email = decoded_value.get("email")
    role = decoded_value.get("role")

    # --------------------------------------------------------
    # Find User
    # --------------------------------------------------------

    result = await db.execute(
        select(UserModel).where(
            UserModel.email == email
        )
    )

    user_model = result.scalars().first()

    if not user_model:
        raise HTTPException(
            status_code=401,
            detail="User Not Found"
        )

    # --------------------------------------------------------
    # Verify Refresh Token from Database
    # --------------------------------------------------------

    if payload.refresh_token != user_model.refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Refresh Token Not Valid"
        )

    # --------------------------------------------------------
    # Create New Access Token
    # --------------------------------------------------------

    access_token = JWTService().Create_Assess_Token(email=email,role=role)

    # --------------------------------------------------------
    # Create New Refresh Token
    # --------------------------------------------------------

    refresh_token = JWTService().Create_Refresh_Token(
        email=email,
        role=role
    )

    # --------------------------------------------------------
    # Store New Refresh Token
    # --------------------------------------------------------

    user_model.refresh_token = refresh_token

    await db.commit()
    await db.refresh(user_model)

    return JWTOut(
        Assess_token=access_token,
        Refresh_token=refresh_token,
        msg="New Tokens Generated Successfully !!!"
    )


# ============================================================
# DELETE USER
# ============================================================

@users.delete(
    "/delete",
    response_model=BaseOut
)
async def Delete_Perticular_User(
    email: EmailStr,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        delete(UserModel)
        .where(UserModel.email == email)
        .returning(UserModel.user_id)
    )

    deleted_user = result.scalar_one_or_none()

    if deleted_user is None:
        raise HTTPException(
            status_code=404,
            detail="Email Not Found"
        )

    await db.commit()

    return BaseOut(
        msg="User Deleted Successfully"
    )


