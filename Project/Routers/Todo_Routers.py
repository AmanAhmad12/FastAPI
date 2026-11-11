# Import :
from fastapi import APIRouter ,Response,Request,HTTPException,Depends
from uuid import UUID , uuid4
from pydantic import BaseModel,Field , ConfigDict 

#for ratelimiting
from slowapi import Limiter
from slowapi.util import get_remote_address

# for db
from models import TodoModel
from sqlalchemy.ext.asyncio import AsyncSession 
from config.db import get_db
from sqlalchemy import select, delete 

# for JWT
from services import JWTService
# from fastapi.security import OAuth2PasswordBearer # used to read tha Bearer Token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials  # 
security = HTTPBearer()
from models import UserModel
#   Checks whether the request contains an Authorization header.
#   Stores the extracted authorization information.
#   HTTPBearer validates and extracts the Authorization: Bearer <token> header,
#   while HTTPAuthorizationCredentials stores the extracted scheme (Bearer) and JWT token (credentials) 
#   so that the application can authenticate and authorize users




# Creating an Object of FastAPI
# todoapp = FastAPI(title="TODO APP",description="TODO APPLICATION TO ADD TARGET LIST",version="1.0.0")

todo_router = APIRouter(prefix="/todo",tags=["todo Route"])

limiter=Limiter(key_func=get_remote_address)

# for JWT
# oauth_schema = OAuth2PasswordBearer(
#     tokenUrl="api/user/signin"    # used to fetch the schema from the valid token generater
# )


# Defining the Structure :
class Todos(BaseModel):
    id : UUID = Field(default_factory=uuid4) # way to create a unique Id, if we simply write uuid4() this will create constant id
    name:str
    category:str
    status:bool =False
    #password:SecretStr

    model_config=ConfigDict(from_attributes=True)

# uses this for input beacuse id is not included therefore we will always get unique id
class TodosCreate(BaseModel):
    name:str
    category:str
    status:bool =False


# Creating the Base pydantic model for the Response
class BaseOut(BaseModel):
    msg:str
    error:str | None=None


#Internal DataBases : 
# db:list[Todos]=[]


# Creating the BaseModel for the Create 
class  CreateTodoOutput(BaseOut):
    List:Todos
    email:str =None
    # api_count:int 


#creating the BaseModel for the deletion
class DeleteTodoOutput(BaseModel):
    id: UUID
    msg: str

# Creating Post Routes  :
@todo_router.post("/create",status_code=201,description="Creating a New List")
@limiter.limit("2/minute")
async def create_todo(request:Request,
        todo:TodosCreate,
        db:AsyncSession=Depends(get_db)
    ) -> CreateTodoOutput | BaseOut:

    # db.append(todo)

    todo_model=TodoModel(**todo.model_dump())  # used to (**)unpack to convert it into dict
    db.add(todo_model)
    await db.commit()
    await db.refresh(todo_model)

    return CreateTodoOutput(
        List=Todos.model_validate(todo_model),
        msg="New List Is Created and Added to the DB"
        # api_count=request.app.state.request_count  
        #request.app: Reference to the main FastAPI() app instance (used to access request.app.state).
    )


# Creating the Get List BaseModel:
class GetTodos(BaseOut):
    Lists:list[Todos]

# Creating dependency
def check_id(id:str): 
    try:
        id=UUID(id)
    except Exception as ex:
        raise HTTPException(
            detail=BaseOut(msg="Wrong UUID!",error=str(ex)).model_dump_json(),
            status_code=400,
        )
    return id


# Logic to get current User 
async def get_current_user(
    # token:str = Depends(oauth_schema)
    bearer_token: HTTPAuthorizationCredentials = Depends(security),  # this object conatin two property(scheme and credentials)
    db:AsyncSession=Depends(get_db)) -> str:
    token = bearer_token.credentials


    payload = JWTService().decode(token=token)


    if payload is None:
        raise HTTPException(      
            detail="Invalid Token !!!",
            status_code=401
        )
    email:str=payload.get("email")

    result=await db.execute(select(UserModel).where(UserModel.email==email))

    user=result.scalars().first()

    if not user:
        raise HTTPException(
            detail="User Not Found !!!",
            status_code=401
        )

    return email

# Creating Get Routes :

@todo_router.get("/todos",response_model=GetTodos | BaseOut ,status_code=200,description="Fetching ALl the Lists")
@limiter.limit("3/minute")
async def get_all(request:Request,db:AsyncSession=Depends(get_db),curr_user:str=Depends(get_current_user)) -> GetTodos | BaseOut:
        # Execute the SQL query:
        # SELECT * FROM todo1
        # and store the result object in todo_db_result#
    todo_db_result = await db.execute(select(TodoModel)) 
        
        # Extract actual TodoModel objects from the result
        # scalars() returns only the model instances
        # all() converts them into a Python list
    todo_models =  todo_db_result.scalars().all()

        # Convert each SQLAlchemy TodoModel object into a Pydantic Todos object
        # using model_validate()
        # The list comprehension loops through all records fetched from the database
    todos :list[Todos] = [Todos.model_validate(todo_model) for todo_model in todo_models]


    return GetTodos(
        Lists=todos,
        msg="SuccessFully Fetched All the Lists !!! "
    )

#------------------------------------------------------------------------------------------

# Creating routes to get perticular List :
@todo_router.get("/todo/{id}",status_code=200,response_model=CreateTodoOutput | BaseOut,description="Fetching a perticular by ID")
async def get_Todo_ID(id:str=Depends(check_id),db:AsyncSession=Depends(get_db),curr_user:str=Depends(get_current_user)) -> CreateTodoOutput | BaseOut:
    # try:
    #     id=UUID(id)                        # we are using removing this we used dependecy injection
    # except Exception as ex:
    #     return Response(
    #         content=BaseOut(msg="Wrong UUID!",error=str(ex)).model_dump_json(),
    #         status_code=400,
    #     )

    todo_specific_result = await db.execute(select(TodoModel).where(TodoModel.id==id)) # explaination in getall endpoint
    todo_model = todo_specific_result.scalar_one_or_none()  # explaination in getall endpoint

    if not todo_model:
        return Response(
        content=BaseOut(msg="Error",error="ID Not Found!!!").model_dump_json(),
        status_code=404,
        media_type="application/json"
    )
    return Response(
        content=CreateTodoOutput(List=todo_model,msg="Particular Todo list Fetched !!!").model_dump_json(),
        status_code=200,
        media_type="application/json"
    )
    

#---------------------------------------------------------------------------------------------

#   Creating the Routing of the Update Method : 

@todo_router.patch("/update_name/{id}",response_model=CreateTodoOutput | BaseOut)

async def Update_Todo_name(newName:str,id:str=Depends(check_id),db:AsyncSession=Depends(get_db)) -> CreateTodoOutput | BaseOut:
    # try:
    #     id=UUID(id)
    # except Exception as ex:               # replace this with DI (id:str=Depends(check_id))
    #     return BaseOut(msg="Wrong UUID!",error=str(ex))

    temp_todo = await db.execute(select(TodoModel).where(TodoModel.id==id)) # execute select + where query 

    fetch_todo_model = temp_todo.scalars().first()

    if not fetch_todo_model:
        return BaseOut(
        msg="Todo Not Found!",
        error="Error!!!!!"
    )

    fetch_todo_model.name=newName

    await db.commit()
    await db.refresh(fetch_todo_model)

    return CreateTodoOutput(
        List=fetch_todo_model,
        msg="Name Updated Successfully !!!"
    )


# Database Row
#       ↓
# Fetch Record
#       ↓
# fetch_todo_model
#       ↓
# fetch_todo_model.name = newName
#       ↓
# Object Marked Dirty
#       ↓
# await db.commit()
#       ↓
# SQLAlchemy Generates UPDATE Query
#       ↓
# PostgreSQL Updated
#       ↓
# await db.refresh()
#       ↓
# Python Object Updated



#Delete Router -- Used to deleted the List

@todo_router.delete("/delete/{id}",response_model=CreateTodoOutput | BaseOut)

async def Delete_particular_todo(id:str=Depends(check_id),db:AsyncSession=Depends(get_db)):
    # try:
    #     id=UUID(id)
    # except Exception as ex:
    #     return BaseOut(msg="Wrong UUID!",error=str(ex))

    temp_todo_id = await db.execute(delete(TodoModel).where(TodoModel.id==id).returning(TodoModel.id))
    # by default delete does not return anything  

    fetch_todo_model_id = temp_todo_id.scalar_one_or_none()
    await db.commit() # to complete the operation without the commit it will lead to error
    if not fetch_todo_model_id:
        return BaseOut(
        msg="Todo Not Found!",
        error="Error!!!!!"
    )
    return DeleteTodoOutput(
        id=fetch_todo_model_id,
        msg= f"TODO deleted Successfully UUID id {fetch_todo_model_id} !!!"
    )



# Creating Route -- That Fetch the todo by category:

@todo_router.get("/category",description="Getting TODO by Category")

async def get_todo_by_category(_category:str,db:AsyncSession=Depends(get_db)):

    temp_todo = await db.execute(select(TodoModel).where(TodoModel.category==_category))

    fetch_todo_model = temp_todo.scalars().first()

    if not fetch_todo_model:
        return BaseOut(
        msg="Failed",
        error="Invalid Category (Category NOT FOUND IN THE DATABASES) !!!"
    )
    return CreateTodoOutput(
        List=fetch_todo_model,
        msg="Successfully TODO Fetched"
    )




