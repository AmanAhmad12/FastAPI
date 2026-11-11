from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID, uuid4
from datetime import date
from fastapi import APIRouter, HTTPException, Response, Request, Depends

from services import Rate_limiter

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from config.db import get_db
from services import get_current_user
from sqlalchemy import select, func
from Models import BudgetModel, ExpenseModel
budget = APIRouter(prefix="/budget", tags=["Budget Route"])


class Budget(BaseModel):
    budget_id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    category_id: UUID
    budget_name: str
    budget_amount: float
    spent_amount: float = 0.0
    remaining_amount: float = 0.0
    start_date: date
    end_date: date
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


DB: list[Budget] = []


class Budget_create(BaseModel):
    user_id: UUID
    category_id: UUID
    budget_name: str
    budget_amount: float
    # spent_amount: float = 0.0
    # remaining_amount: float = 0.0
    start_date: date
    end_date: date
    is_active: bool = True


class Budget_response(BaseModel):
    data: list[Budget]
    msg: str
    error: str = "   ***NO ERROR***   "


@budget.post("/add", response_model=Budget_response)
async def Add_new_Budget(
    newBudget: Budget_create,
    request: Request,
    db: AsyncSession = Depends(get_db),
    curr_user=Depends(get_current_user)
) -> Budget_response:

#        for using internal db

    # for temp in DB:
    #     if(temp.user_id==newBudget.user_id and temp.category_id==newBudget.category_id
    #     and temp.start_date==newBudget.start_date and temp.end_date == newBudget.end_date
    #     ):
    #         raise HTTPException(
    #             detail="Budget Is Already there in DB !!!",
    #             status_code=409
    #         )

    # budget_data = Budget(
    #     user_id=newBudget.user_id,
    #     category_id=newBudget.category_id,
    #     budget_name=newBudget.budget_name,
    #     budget_amount=newBudget.budget_amount,
    #     spent_amount=newBudget.spent_amount,
    #     remaining_amount=newBudget.budget_amount - newBudget.spent_amount,
    #     start_date=newBudget.start_date,
    #     end_date=newBudget.end_date,
    #     is_active=newBudget.is_active
    # )

    # DB.append(budget_data)
    # return Budget_response(
    #     data=[budget_data],
    #     msg="The New Budget Is Added Successfully !!!"
    # )

    if newBudget.start_date > newBudget.end_date:
        raise HTTPException(
            status_code=400,
            detail="Start Date Cannot Be Greater Than End Date !!!"
        )

    expense_result = await db.execute(select(func.sum(ExpenseModel.amount)).where(
            ExpenseModel.user_id == curr_user.user_id,
            ExpenseModel.category_id == newBudget.category_id
        )
    )

    spent_amount = expense_result.scalar()

    if spent_amount is None:
        spent_amount = 0.0

    remaining_amount = (
        newBudget.budget_amount - spent_amount
    )

    data_model = BudgetModel(
        user_id=curr_user.user_id,
        category_id=newBudget.category_id,
        budget_name=newBudget.budget_name,
        budget_amount=newBudget.budget_amount,
        spent_amount=spent_amount,
        remaining_amount=remaining_amount,
        start_date=newBudget.start_date,
        end_date=newBudget.end_date,
        is_active=newBudget.is_active
    )

    db.add(data_model)

    await db.commit()
    await db.refresh(data_model)

    return Budget_response(
        data=[
            Budget.model_validate(data_model)
        ],
        msg="The New Budget Is Added Successfully !!!"
    )

# -------------------------------------------------------------------------------------
@budget.get("/get", response_model=Budget_response)
async def Fetch_budget_by_User_id(
    user_id:UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    curr_user=Depends(get_current_user) # for providing the authanication 
):

    # for the internal db : --------------------------------------------
    # result=[]
    # for temp in DB:
    #     if(temp.user_id==user_id):
    #         result.append(temp)
    # if result:
    #     return Budget_response(
    #         data=result,
    #         msg="Successfully Fetched ALl the Budget !!!",
    #         status_code=200
    #     )
    # raise HTTPException(
    #     detail="USER DOES NOT HAVE ANY BUDGET !!!",
    #     status_code=404
    # )

    # --------------------

    await Rate_limiter(curr_user)

    temp_data = await db.execute(select(BudgetModel).where(BudgetModel.user_id == user_id))

    data_model = temp_data.scalars().all()

    if not data_model:
        return Response(
            content=Budget_response(
                data=[],
                msg="Error",
                error="ID Not Found!!!"
            ).model_dump_json(),
            status_code=404,
            media_type="application/json"
        )

    return Response(
        content=Budget_response(
            data=[
                Budget.model_validate(temp)
                for temp in data_model
            ],
            msg="Particular Budget List Fetched !!!"
        ).model_dump_json(),
        status_code=200,
        media_type="application/json"
    )


@budget.patch("/update/{budget_id}", response_model=Budget_response)
async def Update_the_perticular_budget(
    budget_id: UUID,
    budget_amount: float | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    db: AsyncSession = Depends(get_db),
    request: Request = None
):

#------------------------------------------  for internal db

    # for temp in DB:

    #     if temp.budget_id == budget_id:

    #         if budget_amount is not None:
    #             temp.budget_amount = budget_amount

    #         if start_date is not None:
    #             temp.start_date = start_date

    #         if end_date is not None:
    #             temp.end_date = end_date

    #         if temp.start_date > temp.end_date:
    #             raise HTTPException(
    #                 status_code=400,
    #                 detail="Start date cannot be greater than end date"
    #             )

    #         return Budget_response(
    #             data=[temp],
    #             msg="Budget Updated Successfully !!!",
    #             status_code=200
    #         )

    # raise HTTPException(
    #     status_code=404,
    #     detail="Budget Not Found !!!"
    # )

#------------------------------------------------- for real db

    temp_data = await db.execute(
        select(BudgetModel).where(
            BudgetModel.budget_id == budget_id
        )
    )

    data_model = temp_data.scalar_one_or_none()

    if not data_model:
        return Response(
            content=Budget_response(
                data=[],
                msg="Error",
                error="ID Not Found!!!"
            ).model_dump_json(),
            status_code=404,
            media_type="application/json"
        )

    if budget_amount is not None:
        data_model.budget_amount = budget_amount

    if start_date is not None:
        data_model.start_date = start_date

    if end_date is not None:
        data_model.end_date = end_date

    if data_model.start_date > data_model.end_date:
        return Response(
            content=Budget_response(
                data=[Budget.model_validate(data_model)],
                msg="The Start time is greater than end time",
                error="   ***ERROR***   "
            ).model_dump_json(),
            status_code=400,
            media_type="application/json"
        )

    data_model.remaining_amount = (
        data_model.budget_amount -
        data_model.spent_amount
    )

    await db.commit()
    await db.refresh(data_model)

    return Response(
        content=Budget_response(
            data=[Budget.model_validate(data_model)],
            msg="The data Is Successfully Updated Into the Database !!!"
        ).model_dump_json(),
        status_code=200,
        media_type="application/json"
    )