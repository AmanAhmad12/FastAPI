from fastapi import FastAPI, APIRouter, HTTPException,Request ,Response,Depends
from pydantic import BaseModel,Field ,ConfigDict,Field

categorys = APIRouter(prefix="/category",tags=["Categories Route"])

# for DB configuration 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select , delete
from services import get_current_user
from config.db import get_db
from uuid import UUID, uuid4
from Models import CategoryModel

class Category(BaseModel):
    category_id: UUID = Field(default_factory=uuid4)
    category_name: str
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)

class Category_create(BaseModel): 
    category_name: str


class category_output(BaseModel):
    data:list[Category]=Field(default_factory=list)
    msg:str
    error:str="   ***NO ERROR***   "




# DB:list[Category]=[]


@categorys.post("/create", response_model=category_output)
async def Create_a_new_Category(new_category: Category_create,request:Request,db:AsyncSession=Depends(get_db),curr_user=Depends(get_current_user)):

    # --------------------------------------   For internal db : 

    # for temp in DB:
    #     if (temp.user_id == new_category.user_id and temp.category_name.lower() == new_category.category_name.lower()):
    #         raise HTTPException(
    #             status_code=409,
    #             detail="Category Already Present !!!"
    #         )

    # category = Category(
    #     category_name=new_category.category_name,
    #     user_id=new_category.user_id
    # )

    # DB.append(category)

    # return category_output(
    #     data=[category],
    #     msg="New Category Created Successfully !!!",
    #     error="***NO ERROR***"
    # )

    # ?-----------------------------------------------  for real db  :-----

    data_model = CategoryModel(
        category_name=new_category.category_name,
        user_id=curr_user.user_id
    )

    db.add(data_model)

    await db.commit()
    await db.refresh(data_model)

    return Response(
        content=category_output(
            data=[Category.model_validate(data_model)],
            msg="The New Data Updated on the DB"
        ).model_dump_json(),
        status_code=201,
        media_type="application/json"
    )




# -------------------------------------------------------------------------------------------------------------------



@categorys.get("/get_all",response_model=category_output)
async def Get_all_categories(request:Request,db:AsyncSession=Depends(get_db),curr_user=Depends(get_current_user)):
    #-----------------------------------------  For internal db  :-------------
    # return category_output(
    #     data=DB,
    #     msg=f"{'EMPTY LIST - ' if DB == [] else ''}Successfully Fetched All the Categories",
    #     error="   ***NO ERROR***   "
    # )

    #------------------------------------   for real db  : 

    temp_data = await db.execute(select(CategoryModel))

    data_model = temp_data.scalars().all()

    if not data_model:
        return Response(
            content=category_output(
                msg="No DATA",
                error="   ***NO DATA***   "
            ).model_dump_json(),
            status_code=404,
            media_type="application/json"
        )

    return Response(
        content=category_output(
            data=[
                Category.model_validate(temp)
                for temp in data_model
            ],
            msg="DATA SUCCESSFULLY FETCHED !!!",
            error="***NO ERROR***"
        ).model_dump_json(),
        status_code=200,
        media_type="application/json"
    )

    # --------------------------------------------------------------------------------------------------------------

@categorys.patch("/update/{c_id}",response_model=category_output)
async def Update_the_perticular_categories_By_category_id(c_id:UUID,new_name:str,request:Request,db:AsyncSession=Depends(get_db)):
    # --------------------- for Internal data : ------------------
    # for temp in DB:
    #     if(temp.category_id==c_id):
    #         temp.category_name=new_name
    #         return category_output(
    #             data=[temp],
    #             msg=" Categories Successfully Updated !!!! ",
    #             error="   ***NO ERROR***   "
    #         )
    # raise HTTPException(
    #     detail="Category_ID not Found !!!",
    #     status_code=401
    # )

    # ------------------------------------   for real data :-------------------

    temp_data = await db.execute(select(CategoryModel).where(CategoryModel.category_id==c_id))

    data_model = temp_data.scalar_one_or_none()
    if not data_model:
        return Response(
            content=category_output(
                msg="No DATA",
                error="   ***NO DATA***   "
            ).model_dump_json(),
            status_code=404,
            media_type="application/json"
        )

    data_model.category_name=new_name

    await db.commit()
    await db.refresh(data_model)

    return Response(
        content=category_output(
            data=[Category.model_validate(data_model)],
            msg="DATA UPDATED SUCCESSFULLY !!! "
        ).model_dump_json(),
        status_code=200,
        media_type="application/json"
    )


# ----------------------------------------------------------------------------------------------------------

@categorys.delete("/delete/{category_id}",response_model=category_output)
async def Delete_the_Category_By_Category_ID(category_id:UUID,request:Request,db:AsyncSession=Depends(get_db)):
    # --------- for the internal db : -----
    # for index,temp in enumerate(DB):
    #     if(temp.category_id==category_id):
    #         DB.remove(DB[index])
    #         return category_output(
    #             data=[temp],
    #             msg=" Categories deleted Successfully !!!! ",
    #             error="   ***NO ERROR***   "
    #         )
    # raise HTTPException(
    #     detail="Category_ID not Found !!!",
    #     status_code=401
    # )

    # ==================== for the real Db : ====

    temp_data = await db.execute(delete(CategoryModel).where(CategoryModel.category_id==category_id).returning(CategoryModel.category_id))
    
    data_model = temp_data.scalar_one_or_none()
    if not data_model:
        return Response(
            content=category_output(
                msg="No DATA",
                error="   ***NO DATA***   "
            ).model_dump_json(),
            status_code=404,
            media_type="application/json"
        )
    
    await db.commit()
    return Response(
        content=category_output(
            msg=f"DATA DELETED SUCCESSFULLY OF CATEGORY_ID {data_model}"
        ).model_dump_json(),
        status_code=200,
        media_type="application/json"
    )




# -=======================================================================================================================-


temp_DB:list[Category] =[]
@categorys.get("/get/{user_id}",response_model=category_output)

async def get_all_the_category_by_user_id(user_id:UUID,request:Request,db:AsyncSession=Depends(get_db),curr_user=Depends(get_current_user)):
    
    #  for the internal DB -------------------------


    # for temp in DB:
    #     if(temp.user_id==user_id):
    #         temp_DB.append(temp)
    # if not temp_DB:
    #     raise HTTPException(
    #         detail="The Current User Does not contains any Category !!!",
    #         status_code=401
    #     )
    # return category_output(
    #     data=temp_DB,
    #     msg="Successfullt Fetched all the Category",
    #     error="   ***NO ERROR***   "
    # )

    #  -------------------=------------------- For the real DataBase : 

    temp_data = await db.execute(select(CategoryModel).where(CategoryModel.user_id==curr_user.user_id))

    data_model = temp_data.scalars().all()

    if not data_model:
        return Response(
            content=category_output(
                msg="No DATA",
                error="   ***NO DATA***   "
            ).model_dump_json(),
            status_code=404,
            media_type="application/json"
        )

    return Response(
        content=category_output(
            data=[
                Category.model_validate(temp)
                for temp in data_model
            ],
            msg=f"DATA FETCHED SUCCESSFULLY !!!"
        ).model_dump_json(),
        status_code=200,
        media_type="application/json"
    )
    
