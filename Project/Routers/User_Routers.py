from fastapi import FastAPI ,APIRouter,Depends,Response , HTTPException

from passlib.context import CryptContext   # provide the hasing to the password
from pydantic import BaseModel ,Field,ConfigDict,EmailStr
from uuid import UUID,uuid4
from models import UserModel
from services import HashService,JWTService

from sqlalchemy.ext.asyncio import AsyncSession
from config.db import get_db
from sqlalchemy import select,delete

user_router = APIRouter(prefix="/user",tags=["User Route"])

pwd_context = CryptContext(  
    # which method we are using to encrypting the password
    schemes=["bcrypt"],
    deprecated="auto" 
    # means it used to decrept the password based on the schemes that we used at the time of password encrytion
)

#----------------------------------------------------------------------------------
                    # secret_value = "abcde"

                    # def hash_password(password:str) -> str:   
#  WE HAVE CREATED  #     # encrypting the password
#  THE SERVICE FOR  #     password_concat=password+secret_value
#  THIS CODE        #     return pwd_context.hash(password_concat)

                    # def verify_hash_password(password:str,hash_password:str) -> Boolean:
                    #     password_concat=password + secret_value
                    #     return pwd_context.verify(password_concat,hash_password)
#-----------------------------------------------------------------------------------

class User(BaseModel):
    id:UUID=Field(default_factory=uuid4)
    name:str
    email:EmailStr
    password:str
    refresh_token:str|None=None

    model_config=ConfigDict(from_attributes=True) # understand the SQLALCHEMY format directly

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class BaseOut(BaseModel):
    msg:str
    error:str | None=None

class UserOut(BaseModel):
    id:UUID
    name:str
    email:EmailStr

    model_config = ConfigDict(
        from_attributes=True
    ) #read the data from the SQLALCEHMY obj 

class CreateUserOutput(BaseOut):
    List:UserOut

class SignIn(BaseModel):
    email:EmailStr
    password:str

class JWTOut(BaseOut):
    Assess_token:str
    Refresh_token:str

#creating the routes for the signup(adding new user)
@user_router.post("/signup",response_model=CreateUserOutput)

async def Sign_Up(user:UserCreate,db:AsyncSession=Depends(get_db)):

#   -----------------------------------This will check the User is Already Exits or not -----===

    user_email_found = await db.execute(select(UserModel).where(UserModel.email==user.email)) # this will be on orm 2x format

    user_model = user_email_found.scalars().all() # return the list

    if user_model:
        raise HTTPException(
            detail="User Already available !!!",
            status_code=409  # conflict 
        )
#   -----------------------------------------------------------------------------------------===

    user.password =  HashService(pwd_context=pwd_context).hash_password(user.password)
    # this is encryting the password and insert in into db using below code

    user_model=UserModel(**user.model_dump())  # used to (**)unpack to convert it into dict
    
    db.add(user_model)
    await db.commit()
    await db.refresh(user_model)
    return CreateUserOutput(
        List=UserOut.model_validate(user_model),
        msg="New User List Is Created and Added to the DB"
    )


#------------------------------------------------------------------------------------------
#Creating Refresh Pydantic model :
class RefreshToken(BaseModel):
    refresh_token: str  

#  Creating the refresh end point  : 

@user_router.post("/refresh", response_model=JWTOut)
async def Refresh_Token(payload: RefreshToken,db: AsyncSession = Depends(get_db)):
    decoded_value = JWTService().decode(
        token=payload.refresh_token
    )

    if decoded_value is None:
        

    email: str = decoded_value.get("email")

    result = await db.execute(
        select(UserModel).where(
            UserModel.email == email
        )
    )

    user_model = result.scalars().first()

    if not user_model:
        raise HTTPException(
            status_code=401,
            detail="User Not Found !!!"
        )


    if payload.refresh_token != user_model.refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Given Refresh Token is not Valid !!!"
        )

    assess_token = JWTService().Create_Assess_Token(email=email) 
    refresh_token = JWTService().Create_Refresh_Token(email=email) 

    await db.commit()
    await db.refresh(user_model)

    
    return JWTOut(
        Assess_token=assess_token,
        Refresh_token=payload.refresh_token,
        msg="Assess Token Generated Successfully !!!"
    )



                            # Login
                            #   ↓
                            # Access Token (5 min)
                            # Refresh Token (7 days)
                            #   ↓
                            # Call Protected API
                            #   ↓
                            # Access Token Expired
                            #   ↓
                            # 401 Unauthorized
                            #   ↓
                            # Call /refresh
                            #   ↓
                            # Get New Access Token
                            #   ↓
                            # Retry Original API





#------------------------------------------------------------------------------------------------------------------

#Creating the routes for the Signin
@user_router.post("/signin",response_model=JWTOut)

async def SignIn_user(user:SignIn, db:AsyncSession=Depends(get_db)):

    temp_db_result = await  db.execute(select(UserModel).where(UserModel.email==user.email))

    temp_data = temp_db_result.scalars().first()  #usermodel variable name

    if not temp_data:
        raise HTTPException(
            detail="User Not Found",
            status_code=404
        )
    temp_user = User.model_validate(temp_data) # this line is converting the data from list to Pydantic format
    
    user_login_bool = HashService(pwd_context=pwd_context).verify_hash_password(
        user.password, # Current Password
        temp_user.password  # Pre Stored Password
    ) # logic to compare the password from the db and currect entered password

    if not user_login_bool:
        raise HTTPException(
            detail="User's Password is Incorrect !!!",
            status_code=401 # unauthoraised user 
        )

    assess_token = JWTService().Create_Assess_Token(email=user.email)
    refresh_token = JWTService().Create_Refresh_Token(email=user.email)

    # save Refersh token in db :
    temp_data.refresh_token=refresh_token   
    await db.commit()  # updated on db
    await db.refresh(temp_data)



    return JWTOut(
        Assess_token=assess_token,
        Refresh_token=refresh_token,
        msg="User Login Successfully !!! "
    )


# to delete the user usinf email id : 
@user_router.delete("/delete", response_model=BaseOut)

async def Delete_Perticular_User(email: EmailStr,db: AsyncSession = Depends(get_db)):

    result = await db.execute(
        delete(UserModel)
        .where(UserModel.email == email)
        .returning(UserModel.id)
    )

    deleted_id = result.scalar_one_or_none()

    if deleted_id is None:
        raise HTTPException(
            status_code=404,
            detail="Email Does Not Exist"
        )

    await db.commit()

    return BaseOut(
        msg="User Data Successfully Deleted"
    )




#-----------------------------------------------------------------------------------------------------------
#                       EXPLANATION :                   
#-----------------------------------------------------------------------------------------------------------

                        # ========================= USER ROUTER =========================
                    # Handles all user-related operations:
                    # 1. User Registration (Signup)
                    # 2. User Authentication (Signin)
                    # 3. User Deletion

                    # APIRouter groups all user APIs under /user prefix.


                    # ========================= PASSWORD SECURITY =========================
                    # CryptContext is responsible for:
                    # - Hashing passwords before storing in DB
                    # - Verifying entered passwords during login
                    #
                    # bcrypt algorithm:
                    # Plain Password
                    #      ↓
                    # Encrypted/Hashed Password
                    #      ↓
                    # Stored in Database


                    # ========================= USER MODEL (PYDANTIC) =========================
                    # Used for converting SQLAlchemy ORM objects into Pydantic objects.
                    #
                    # from_attributes=True :
                    # Allows Pydantic to read data directly from SQLAlchemy objects.
                    #
                    # Example:
                    # UserModel (ORM)
                    #       ↓
                    # User.model_validate()
                    #       ↓
                    # User (Pydantic)


                    # ========================= USERCREATE =========================
                    # Request model for Signup.
                    #
                    # Why no ID?
                    # - Client should not send UUID.
                    # - Database automatically creates UUID.
                    # - Prevents users from providing custom IDs.


                    # ========================= USEROUT =========================
                    # Response model.
                    #
                    # Purpose:
                    # - Return safe user information.
                    # - Password is excluded.
                    #
                    # Returned Fields:
                    # - id
                    # - name
                    # - email


                    # ========================= BASEOUT =========================
                    # Common response schema.
                    #
                    # Used to send:
                    # - Success Message
                    # - Error Message
                    #
                    # Creates a consistent API response format.


                    # ========================= SIGNUP FLOW =========================
                    #
                    # Step 1:
                    # Receive name, email and password.
                    #
                    # Step 2:
                    # Check whether email already exists.
                    #
                    # Purpose:
                    # Avoid duplicate user creation.
                    #
                    # Step 3:
                    # Hash password using HashService.
                    #
                    # Purpose:
                    # Never store plain-text passwords.
                    #
                    # Step 4:
                    # Convert Pydantic model → SQLAlchemy model.
                    #
                    # Step 5:
                    # Add object to DB Session.
                    #
                    # Step 6:
                    # Commit transaction.
                    #
                    # Purpose:
                    # Permanently save data into database.
                    #
                    # Step 7:
                    # Refresh object.
                    #
                    # Purpose:
                    # Retrieve generated values such as UUID.
                    #
                    # Step 8:
                    # Convert SQLAlchemy object → UserOut response model.
                    #
                    # Step 9:
                    # Return success response.


                    # ========================= SIGNIN FLOW =========================
                    #
                    # Step 1:
                    # Receive email and password.
                    #
                    # Step 2:
                    # Search user using email.
                    #
                    # Step 3:
                    # If email not found:
                    # Return 404 Not Found.
                    #
                    # Step 4:
                    # Verify password.
                    #
                    # Current Password
                    #        ↓
                    # HashService
                    #        ↓
                    # Compare With Stored Hash
                    #        ↓
                    # True / False
                    #
                    # Step 5:
                    # If password mismatch:
                    # Return 401 Unauthorized.
                    #
                    # Step 6:
                    # If password matches:
                    # Return Login Success.


                    # ========================= DELETE USER FLOW =========================
                    #
                    # Step 1:
                    # Receive user email.
                    #
                    # Step 2:
                    # Execute DELETE query.
                    #
                    # Step 3:
                    # Use returning(id).
                    #
                    # Purpose:
                    # Check whether a record was actually deleted.
                    #
                    # Step 4:
                    # If id is None:
                    # User does not exist.
                    #
                    # Step 5:
                    # Commit transaction.
                    #
                    # Purpose:
                    # Permanently remove the user.
                    #
                    # Without Commit:
                    # DELETE
                    #    ↓
                    # ROLLBACK
                    #    ↓
                    # Record remains in DB
                    #
                    # With Commit:
                    # DELETE
                    #    ↓
                    # COMMIT
                    #    ↓
                    # Record removed permanently


                    # ========================= OVERALL FLOW =========================
                    #
                    # Client Request
                    #        ↓
                    # FastAPI Route
                    #        ↓
                    # Pydantic Validation
                    #        ↓
                    # SQLAlchemy Async Session
                    #        ↓
                    # PostgreSQL Database
                    #        ↓
                    # SQLAlchemy ORM Object
                    #        ↓
                    # Pydantic Response Model
                    #        ↓
                    # API Response

                    #----------------------------------------------------------------------------------------------