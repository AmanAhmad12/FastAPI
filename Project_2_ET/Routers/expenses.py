from fastapi import FastAPI , HTTPException ,APIRouter ,Response,Request,Depends
from pydantic import BaseModel,Field,ConfigDict
from datetime import datetime
from uuid import UUID , uuid4

from config.db import get_db

#    for the db connection  :

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,delete
from services import get_current_user
from Models import ExpenseModel


expense = APIRouter(prefix="/expense",tags=["Expense Route"]) 


class Expenses(BaseModel):
    expense_id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    category_id: UUID
    amount: float
    description: str
    payment_method: str
    expense_date: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(from_attributes=True)

class Expenses_create(BaseModel):
    user_id:UUID
    category_id:UUID
    amount:float
    description:str
    payment_method:str

class Expense_output(BaseModel):
    data:list[Expenses]=Field(default_factory=list)
    msg:str
    error:str="   ***NO ERROR***   "

# DB:list[Expenses]=[]

@expense.post("/add",response_model=Expense_output)

async def Add_New_Expense_Source(newExpense:Expenses_create,request:Request,db:AsyncSession=Depends(get_db)):
    #    For the internal DB : --------------
    # for temp in DB:
    #     if (temp.user_id == newExpense.user_id and temp.category_id == newExpense.category_id and temp.amount == newExpense.amount and temp.description == newExpense.description ):
    #         raise HTTPException(
    #             status_code=409,
    #             detail="Expense Already Present !!!"
    #         )
    # # import to convert like this because db has Expense datatype
    # expense_data = Expenses(
    #     user_id=newExpense.user_id,
    #     category_id=newExpense.category_id,
    #     amount=newExpense.amount,
    #     description=newExpense.description,
    #     payment_method=newExpense.payment_method
    # )
 
    # DB.append(expense_data)
    # return Expense_output(
    #     data=[expense_data],
    #     msg="This Expense Is Already Present In the DataBases !!!",
    # )

#   For the real DATABASES : ===========

    data_model = ExpenseModel(**newExpense.model_dump())

    db.add(data_model)

    await db.commit()
    await db.refresh(data_model)

    return Response(
        content = Expense_output(
            data=[Expenses.model_validate(data_model)],
            msg= "data Added Successfully into the Database !!!",
        ).model_dump_json(),
        status_code=201,
        media_type="application/json"
    ) 

# ?=============================================                  ===================================================================

@expense.get("/get/{user_id}",response_model=Expense_output)
async def Get_The_all_the_expenses_For_perticular_User(user_id:UUID,request:Request,db:AsyncSession=Depends(get_db),curr_user=Depends(get_current_user)):

    # FOR THE INTRERNAL DB : ------------------------
    # result=[]
    # for temp in DB:
    #     if(temp.user_id==user_id):
    #         result.append(temp)
    #         return Expense_output(
    #             data=result,
    #             msg="Successfully Fetched All the Expenses !!!"
    #         )
    # raise HTTPException(
    #     detail="USER NOT FOUND !!!",
    #     status_code=404
    # )

    #  FOR THE REAL DATABASES : ------------------------------------------

    temp_data = await db.execute(select(ExpenseModel).where(ExpenseModel.user_id==curr_user.user_id))

    data_model = temp_data.scalars().all()

    if not data_model:
        return Response(
        content = Expense_output(
            data=[],
            msg= "ERROR",
            error="USER NOT FOUND !!!"
        ).model_dump_json(),
        status_code=404,
        media_type="application/json"
    ) 

    return Response(
        content = Expense_output(
            data=[Expenses.model_validate(temp) for temp in data_model],
            msg= "data Successfully Fetched from the Database !!!",
        ).model_dump_json(),
        status_code=200,
        media_type="application/json"
    ) 

# ===================================================================                ============================================

@expense.patch("/update/{expense_id}", response_model=Expense_output)
async def Update_the_perticular_Expense_Source_OR_Expense_amount(
    expense_id: UUID,
    request: Request,
    amount: float = 0.0,
    description: str | None = None,
    db: AsyncSession = Depends(get_db),
    curr_user=Depends(get_current_user)
):

    #     For the INTERNAL db : ======-----------------------------------

    # for temp in DB:

    #     if temp.expense_id == expense_id:

    #         if amount != 0.0:
    #             temp.amount = amount

    #         if description is not None:
    #             temp.description = description

    #         return Expense_output(
    #             data=[temp],
    #             msg="Successfully Updated !!!"
    #         )

    # raise HTTPException(
    #     detail="Expense ID Not Found !!!",
    #     status_code=404
    # )

    # --------------------------- for THE REAL DATABASES :----------------------------------------- -

    temp_data = await db.execute(select(ExpenseModel).where(ExpenseModel.expense_id==expense_id,ExpenseModel.user_id == curr_user.user_id))

    data_model = temp_data.scalar_one_or_none()

    if not data_model:
        return Response(
        content = Expense_output(
            data=[],
            msg= "ERROR",
            error="Expense_ID NOT FOUND !!!"
        ).model_dump_json(),
        status_code=404,
        media_type="application/json"
    ) 

    if amount!=0.0 :
        data_model.amount=amount
    if description is not None:
        data_model.description=description

    await db.commit()
    await db.refresh(data_model)
    
    return Response(
        content = Expense_output(
            data=[Expenses.model_validate(data_model)],
            msg= "data Successfully Fetched Updated into Database !!!",
        ).model_dump_json(),
        status_code=200,
        media_type="application/json"
    ) 
    


# ==================================================================== =     ==================================


@expense.delete("/delete/{expense_id}",response_model=Expense_output)
async def Delete_the_Expense_By_Expense_ID(expense_id:UUID,request:Request, db:AsyncSession=Depends(get_db)):

    #  fOR THE DUMMY DATABASE : --------------------------------

    # for index,temp in enumerate(DB):
    #     if(temp.expense_id==expense_id):
    #         DB.remove(DB[index])
    #         return Expense_output(
    #             data=[temp],
    #             msg="Successfully deleted !!!"
    #     )
    # raise HTTPException(
    #     detail="Expense_ID not Found !!!",
    #     status_code=401
    # )     

    # FOR THE REAL DATABASE : -------------------------------

    temp_data = await db.execute(delete(ExpenseModel).where(ExpenseModel.expense_id==expense_id).returning(ExpenseModel.expense_id))

    data_model = temp_data.scalar_one_or_none()

    if not data_model :
        return Response(
        content = Expense_output(
            data=[],
            msg= "ERROR",
            error="Expense_ID NOT FOUND !!!"
        ).model_dump_json(),
        status_code=404,
        media_type="application/json"
    ) 

    await db.commit()

    return Response(
        content = Expense_output(
            msg= "data Successfully deleted from the Database !!!",
        ).model_dump_json(),
        status_code=200,
        media_type="application/json"
    ) 